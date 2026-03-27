import logging
from dataclasses import dataclass
from typing import Any, Type, TypedDict

from core.models import ObjectType
from django import forms
from django.contrib import messages
from django.db import models
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from netbox.views.generic import (
    ObjectDeleteView,
    ObjectEditView,
    ObjectListView,
    ObjectView,
)
from utilities.views import ViewTab, register_model_view

from netbox_ninja_plugin.helpers import (
    get_filter_variable_name,
    get_string_filter_variable_name,
    get_target_model_object_types,
    get_viewable_queryset_for_user,
)
from netbox_ninja_plugin.ninja_template.filtersets import (
    NinjaTemplateFilterSet,
    NinjaTemplateStringFilterFilterSet,
    NinjaTemplateStringFilterOptionFilterSet,
)
from netbox_ninja_plugin.ninja_template.forms import (
    NinjaTemplateFilterForm,
    NinjaTemplateForm,
    NinjaTemplateStringFilterFilterForm,
    NinjaTemplateStringFilterForm,
    NinjaTemplateStringFilterOptionFilterForm,
    NinjaTemplateStringFilterOptionForm,
    NinjaTemplateStringFilterOptionFormSet,
)
from netbox_ninja_plugin.ninja_template.models import (
    NinjaTemplate,
    NinjaTemplateStringFilter,
    NinjaTemplateStringFilterOption,
)
from netbox_ninja_plugin.ninja_template.tables import (
    NinjaTemplateStringFilterOptionTable,
    NinjaTemplateStringFilterTable,
    NinjaTemplateTable,
)

logger = logging.getLogger(__name__)


class NinjaTabDynamicFilterForm(forms.Form):
    """Dynamic object filter form rendered on Ninja tabs."""

    def __init__(
        self,
        *args,
        filter_var_defs: list["TemplateFilterVarDef"],
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        for filter_var_def in filter_var_defs:
            query_key = filter_var_def["template_filter_query_key"]
            field_class = filter_var_def["field_class"]
            field_kwargs = filter_var_def["field_kwargs"]
            self.fields[query_key] = field_class(**field_kwargs)


class TemplateFilterVarDef(TypedDict):
    """
    Minimal schema used to dynamically create filter form fields.

    `selected_pks` / `filter_type` used to exist here but are not required because
    the form is bound directly from `request.GET`.
    """

    filter_variable_name: str
    template_filter_query_key: str
    field_class: type[forms.Field]
    field_kwargs: dict[str, Any]


def _get_template_filter_query_key(
    ninja_template: NinjaTemplate, filter_key: str
) -> str:
    """Build a template-scoped query-string key for a filter variable."""
    return f"t{ninja_template.pk}__{filter_key}"


@dataclass
class NinjaTemplateCard:
    """
    Template rendering context wrapper.

    We keep the original NinjaTemplate instance for rendering (`obj.render`) and URL
    helpers, while attaching precomputed filter metadata required by the template.
    """

    template: NinjaTemplate
    filter_var_defs: list[TemplateFilterVarDef]
    own_filter_query_keys: list[str]
    active_filter_count: int
    has_active_filters: bool
    filter_form: NinjaTabDynamicFilterForm
    filter_values: dict[str, Any]

    def __getattr__(self, name: str):
        # Delegate everything we don't explicitly define to the underlying template.
        return getattr(self.template, name)


def _build_template_filter_var_defs(
    ninja_template: NinjaTemplate, request: HttpRequest
) -> list[TemplateFilterVarDef]:
    """Construct filter variable definitions for a single Ninja template card."""
    filter_var_defs = []

    for object_type_filter in ninja_template.object_type_filters.all():
        filter_variable_name = get_filter_variable_name(object_type_filter)

        # Prefix query keys with template ID to avoid key collisions
        # when multiple templates render filters on the same page.
        template_filter_query_key = _get_template_filter_query_key(
            ninja_template, filter_variable_name
        )

        # Resolve model behind the ObjectType filter. Skip invalid/removed models.
        model_class = object_type_filter.model_class()
        if model_class is None:
            continue

        # This definition is consumed by NinjaTabDynamicFilterForm to create
        # native ModelMultipleChoiceField dynamically.
        filter_var_defs.append(
            {
                "filter_variable_name": filter_variable_name,
                "template_filter_query_key": template_filter_query_key,
                "field_class": forms.ModelMultipleChoiceField,
                "field_kwargs": {
                    "required": False,
                    "queryset": get_viewable_queryset_for_user(
                        model_class, request.user
                    ).order_by("pk"),
                    "label": str(model_class._meta.verbose_name).title(),
                    "widget": forms.SelectMultiple(
                        attrs={
                            "class": "form-select",
                        }
                    ),
                },
            }
        )

    for string_filter in ninja_template.string_filters.all():
        filter_variable_name = get_string_filter_variable_name(string_filter.key)
        template_filter_query_key = _get_template_filter_query_key(
            ninja_template, filter_variable_name
        )

        filter_var_defs.append(
            {
                "filter_variable_name": filter_variable_name,
                "template_filter_query_key": template_filter_query_key,
                "field_class": forms.MultipleChoiceField,
                "field_kwargs": {
                    "required": False,
                    "choices": [
                        (option.value, option.label or option.value)
                        for option in string_filter.options.all()
                    ],
                    "label": string_filter.name,
                    "widget": forms.SelectMultiple(
                        attrs={
                            "class": "form-select",
                        }
                    ),
                },
            }
        )

    return filter_var_defs


def _bind_template_filter_form(
    request: HttpRequest, filter_var_defs: list[dict[str, Any]]
) -> NinjaTabDynamicFilterForm:
    """Bind the dynamic template filter form to request.GET."""
    return NinjaTabDynamicFilterForm(
        request.GET or None,
        filter_var_defs=filter_var_defs,
    )


def _compute_filter_values(
    filter_form: NinjaTabDynamicFilterForm,
    filter_var_defs: list[dict[str, Any]],
) -> dict[str, Any]:
    """Compute filter variable values for a template card."""
    # Default each filter variable to None (means "no filtering" downstream).
    filter_values = {
        filter_var_def["filter_variable_name"]: None
        for filter_var_def in filter_var_defs
    }
    query_key_to_filter_variable_name = {
        filter_var_def["template_filter_query_key"]: filter_var_def[
            "filter_variable_name"
        ]
        for filter_var_def in filter_var_defs
    }

    if filter_form.is_valid():
        # cleaned_data values are QuerySets for object filters and lists
        # for string filters. Keep empty selections as None.
        for query_key, selected_objects in filter_form.cleaned_data.items():
            filter_variable_name = query_key_to_filter_variable_name[query_key]
            if isinstance(selected_objects, models.QuerySet):
                filter_values[filter_variable_name] = (
                    selected_objects if selected_objects.exists() else None
                )
            else:
                filter_values[filter_variable_name] = (
                    selected_objects if selected_objects else None
                )

    return filter_values


@register_model_view(NinjaTemplate)
class NinjaTemplateView(ObjectView):
    queryset = NinjaTemplate.objects.all()
    template_name = "netbox_ninja_plugin/ninjatemplate.html"

    def get_extra_context(
        self, request: HttpRequest, instance: NinjaTemplate
    ) -> dict[str, Any]:
        filter_var_defs = _build_template_filter_var_defs(instance, request)

        own_filter_query_keys = [
            filter_var_def["template_filter_query_key"]
            for filter_var_def in filter_var_defs
        ]

        active_filter_count = sum(
            1
            for filter_var_def in filter_var_defs
            if request.GET.getlist(filter_var_def["template_filter_query_key"])
        )
        has_active_filters = active_filter_count > 0

        filter_form = _bind_template_filter_form(request, filter_var_defs)
        filter_values = _compute_filter_values(
            filter_form=filter_form,
            filter_var_defs=filter_var_defs,
        )

        return {
            "ninja_template_card": NinjaTemplateCard(
                template=instance,
                filter_var_defs=filter_var_defs,
                own_filter_query_keys=own_filter_query_keys,
                active_filter_count=active_filter_count,
                has_active_filters=has_active_filters,
                filter_form=filter_form,
                filter_values=filter_values,
            )
        }


class NinjaTemplateListView(ObjectListView):
    queryset = NinjaTemplate.objects.all()
    table = NinjaTemplateTable
    filterset = NinjaTemplateFilterSet
    filterset_form = NinjaTemplateFilterForm


@register_model_view(NinjaTemplate, "edit")
class NinjaTemplateEditView(ObjectEditView):
    queryset = NinjaTemplate.objects.all()
    form = NinjaTemplateForm


@register_model_view(NinjaTemplate, "delete")
class NinjaTemplateDeleteView(ObjectDeleteView):
    queryset = NinjaTemplate.objects.all()


@register_model_view(NinjaTemplateStringFilter)
class NinjaTemplateStringFilterView(ObjectView):
    queryset = NinjaTemplateStringFilter.objects.all()


class NinjaTemplateStringFilterListView(ObjectListView):
    queryset = NinjaTemplateStringFilter.objects.all()
    table = NinjaTemplateStringFilterTable
    filterset = NinjaTemplateStringFilterFilterSet
    filterset_form = NinjaTemplateStringFilterFilterForm


@register_model_view(NinjaTemplateStringFilter, "edit")
class NinjaTemplateStringFilterEditView(ObjectEditView):
    queryset = NinjaTemplateStringFilter.objects.all()
    form = NinjaTemplateStringFilterForm
    template_name = "netbox_ninja_plugin/ninjatemplatestringfilter_edit.html"

    def _get_instance(self, kwargs):
        pk = kwargs.get("pk")
        if pk is None:
            return None
        return get_object_or_404(self.queryset, pk=pk)

    def _get_context_object(self, instance):
        # NetBox's generic edit template expects an object-like value for metadata.
        return instance if instance is not None else self.queryset.model()

    def get(self, request: HttpRequest, *args, **kwargs):
        instance = self._get_instance(kwargs)
        form = self.form(instance=instance)
        formset = NinjaTemplateStringFilterOptionFormSet(
            instance=instance,
            prefix="options",
        )
        return render(
            request,
            self.template_name,
            {
                "object": self._get_context_object(instance),
                "model": self.queryset.model,
                "form": form,
                "options_formset": formset,
            },
        )

    def post(self, request: HttpRequest, *args, **kwargs):
        instance = self._get_instance(kwargs)
        if instance is not None and instance.pk and hasattr(instance, "snapshot"):
            instance.snapshot()

        form = self.form(request.POST, instance=instance)
        formset = NinjaTemplateStringFilterOptionFormSet(
            request.POST,
            instance=instance,
            prefix="options",
        )

        if form.is_valid() and formset.is_valid():
            form.instance._changelog_message = form.cleaned_data.pop(
                "changelog_message", ""
            )
            string_filter = form.save()
            formset.instance = string_filter
            formset.save()
            messages.success(request, "String filter saved.")
            return HttpResponseRedirect(string_filter.get_absolute_url())

        return render(
            request,
            self.template_name,
            {
                "object": self._get_context_object(instance),
                "model": self.queryset.model,
                "form": form,
                "options_formset": formset,
            },
        )


@register_model_view(NinjaTemplateStringFilter, "delete")
class NinjaTemplateStringFilterDeleteView(ObjectDeleteView):
    queryset = NinjaTemplateStringFilter.objects.all()


@register_model_view(NinjaTemplateStringFilterOption)
class NinjaTemplateStringFilterOptionView(ObjectView):
    queryset = NinjaTemplateStringFilterOption.objects.all()


class NinjaTemplateStringFilterOptionListView(ObjectListView):
    queryset = NinjaTemplateStringFilterOption.objects.all()
    table = NinjaTemplateStringFilterOptionTable
    filterset = NinjaTemplateStringFilterOptionFilterSet
    filterset_form = NinjaTemplateStringFilterOptionFilterForm


@register_model_view(NinjaTemplateStringFilterOption, "edit")
class NinjaTemplateStringFilterOptionEditView(ObjectEditView):
    queryset = NinjaTemplateStringFilterOption.objects.all()
    form = NinjaTemplateStringFilterOptionForm


@register_model_view(NinjaTemplateStringFilterOption, "delete")
class NinjaTemplateStringFilterOptionDeleteView(ObjectDeleteView):
    queryset = NinjaTemplateStringFilterOption.objects.all()


def _register_ninja_tab_view(netbox_model):

    @register_model_view(netbox_model, name="ninjaview", path="ninja")
    class DynamicNinjaView(ObjectView):
        """
        Dynamic view for rendering Ninja templates for specific Netbox objects.
        This view is automatically created for each supported model type.
        """

        queryset = netbox_model.objects.all()
        tab = ViewTab(
            label="Ninja",
            weight=10000,
        )

        model_class: Type[models.Model] = netbox_model

        # pylint: disable=arguments-differ
        def get(self, request: HttpRequest, pk: Any, **kwargs) -> HttpResponse:
            """
            Handle GET requests for Ninja template rendering.
            """
            # Resolve current object type so we can fetch templates linked to this model.
            object_type = ObjectType.objects.get_for_model(self.model_class)
            ninja_templates = object_type.ninja_templates.all().prefetch_related(
                "object_type_filters",
                "string_filters",
                "string_filters__options",
            )
            ninja_templates_list = list(ninja_templates)
            target_object = get_object_or_404(self.model_class, pk=pk)
            ninja_template_cards: list[NinjaTemplateCard] = []

            # Per template "card" we build everything the `ninja_tab.html` template needs:
            # 1) Filter variable definitions from the template's related filters
            #    (`object_type_filters` + `string_filters`). These definitions drive dynamic
            #    Django form field creation (see `NinjaTabDynamicFilterForm`).
            # 2) Query-key bookkeeping so the page can re-render the correct filter widgets
            #    without cross-template key collisions (`own_filter_query_keys`) and show
            #    whether any filter is active (`active_filter_count`).
            # 3) Bind the dynamic GET form to the current request (`request.GET`) so the
            #    user's selected values persist across reloads.
            # 4) Compute `filter_values` (what we pass to `render_object`) using the form's
            #    cleaned data; empty selections become `None` to mean "no filtering".
            for ninja_template in ninja_templates_list:

                filter_var_defs = _build_template_filter_var_defs(
                    ninja_template, request
                )

                own_filter_query_keys = [
                    filter_var_def["template_filter_query_key"]
                    for filter_var_def in filter_var_defs
                ]

                active_filter_count = sum(
                    1
                    for filter_var_def in filter_var_defs
                    if request.GET.getlist(filter_var_def["template_filter_query_key"])
                )

                has_active_filters = active_filter_count > 0

                filter_form = _bind_template_filter_form(request, filter_var_defs)
                filter_values = _compute_filter_values(
                    filter_form=filter_form,
                    filter_var_defs=filter_var_defs,
                )

                ninja_template_cards.append(
                    NinjaTemplateCard(
                        template=ninja_template,
                        filter_var_defs=filter_var_defs,
                        own_filter_query_keys=own_filter_query_keys,
                        active_filter_count=active_filter_count,
                        has_active_filters=has_active_filters,
                        filter_form=filter_form,
                        filter_values=filter_values,
                    )
                )

            return render(
                request,
                "netbox_ninja_plugin/ninja_tab.html",
                {
                    "object": target_object,
                    "ninja_templates": ninja_template_cards,
                    "tab": self.tab,
                },
            )

    DynamicNinjaView.__name__ = f"Ninja{netbox_model.__name__}View"


for model in get_target_model_object_types():
    _register_ninja_tab_view(model)
