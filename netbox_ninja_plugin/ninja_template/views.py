import logging
from typing import Any, Type

from core.models import ObjectType
from django.db import models
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from netbox.views.generic import (
    ObjectChangeLogView,
    ObjectDeleteView,
    ObjectEditView,
    ObjectListView,
    ObjectView,
)
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.views import APIView
from utilities.views import ViewTab, register_model_view

from netbox_ninja_plugin.helpers import get_target_model_object_types
from netbox_ninja_plugin.ninja_template.choices import NinjaTemplateOutputTypeChoices
from netbox_ninja_plugin.ninja_template.filtersets import NinjaTemplateFilterSet
from netbox_ninja_plugin.ninja_template.forms import (
    NinjaTemplateFilterForm,
    NinjaTemplateForm,
)
from netbox_ninja_plugin.ninja_template.models import NinjaTemplate
from netbox_ninja_plugin.ninja_template.tables import NinjaTemplateTable

logger = logging.getLogger(__name__)


@register_model_view(NinjaTemplate)
class NinjaTemplateView(ObjectView):
    queryset = NinjaTemplate.objects.all()
    template_name = "ninja_template.html"


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


@register_model_view(NinjaTemplate, "changelog", kwargs={"model": NinjaTemplate})
class NinjaTemplateChangeLogView(ObjectChangeLogView):
    base_template = "ninja_template.html"


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

            Args:
                request: The HTTP request
                pk: Primary key of the target object
                **kwargs: Additional keyword arguments

            Returns:
                HttpResponse: Rendered template or redirect
            """
            object_type = ObjectType.objects.get_for_model(self.model_class)
            ninja_templates = object_type.ninja_templates.all()
            target_object = self.model_class.objects.get(pk=pk)

            return render(
                request,
                "ninja_tab.html",
                {
                    "object": target_object,
                    "ninja_templates": ninja_templates,
                    "tab": self.tab,
                },
            )

    DynamicNinjaView.__name__ = f"Ninja{netbox_model.__name__}View"


def _get_read_permission_class(netbox_model):
    class HasModelViewPermission(BasePermission):
        def has_permission(self, request, view):
            app_label = netbox_model._meta.app_label
            model_name = netbox_model._meta.model_name
            perm = f"{app_label}.view_{model_name}"
            return request.user.has_perm(perm)

    return HasModelViewPermission


def _register_ninja_api_view(netbox_model):

    permission_class = _get_read_permission_class(model)

    @register_model_view(netbox_model, name="api", path="ninja-api")
    class DynamicNinjaAPIView(APIView):
        permission_classes = [IsAuthenticated, permission_class]

        target_model = netbox_model

        def get(self, request, pk):
            template_id = request.GET.get("template")
            template = get_object_or_404(NinjaTemplate, pk=template_id)

            ninja_template_object_type = ObjectType.objects.get_for_model(NinjaTemplate)
            target_model = get_object_or_404(self.target_model, pk=pk)
            target_object_type = ObjectType.objects.get_for_model(target_model)
            templates_object_types = template.object_types.all()

            # Check that if the template doesn't have any object types, template
            # can only be rendered to a NinjaTemplate object type:
            unassigned_ninja_template = False
            if (
                not templates_object_types
                and target_object_type == ninja_template_object_type
                and str(pk) == str(template_id)
            ):
                unassigned_ninja_template = True

            # Check that the selected template is applied to this object type:
            if (
                not unassigned_ninja_template
                and target_object_type not in templates_object_types
            ):
                raise Http404(
                    f"Selected template is not applied to {target_object_type}."
                )

            data, status = template.render(**{"target_object": target_model})
            http_content_type = "text/plain"
            if template.output_type == NinjaTemplateOutputTypeChoices.JSON:
                http_content_type = "application/json"
            elif template.output_type == NinjaTemplateOutputTypeChoices.DRAW_IO:
                http_content_type = "image/svg+xml"

            return HttpResponse(data, http_content_type, 200 if status else 400)

    DynamicNinjaAPIView.__name__ = f"NinjaAPI{netbox_model.__name__}View"


for model in get_target_model_object_types():
    _register_ninja_tab_view(model)

for model in get_target_model_object_types() + [NinjaTemplate]:
    _register_ninja_api_view(model)
