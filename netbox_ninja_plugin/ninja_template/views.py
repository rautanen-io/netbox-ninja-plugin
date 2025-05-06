import logging
from typing import Any, Type

from core.models import ObjectType
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from netbox.views.generic import (
    ObjectChangeLogView,
    ObjectDeleteView,
    ObjectEditView,
    ObjectListView,
    ObjectView,
)
from utilities.views import ViewTab, register_model_view

from netbox_ninja_plugin.helpers import get_target_model_object_types
from netbox_ninja_plugin.ninja_template.filtersets import NinjaTemplateFilterSet
from netbox_ninja_plugin.ninja_template.forms import (
    NinjaTemplateFilterForm,
    NinjaTemplateForm,
)
from netbox_ninja_plugin.ninja_template.models import NinjaTemplate
from netbox_ninja_plugin.ninja_template.tables import NinjaTemplateTable

logger = logging.getLogger(__name__)


class NinjaTemplateView(ObjectView):
    queryset = NinjaTemplate.objects.all()
    template_name = "ninja_template.html"


class NinjaTemplateRenderView(ObjectView):
    queryset = NinjaTemplate.objects.all()
    template_name = "ninja_template.html"

    def get(self, request, **kwargs):
        instance = self.get_object(**kwargs)
        return render(
            request,
            "ninja_rendered.html",
            {"ninja_template": instance, "target_object": instance},
        )


class NinjaTemplateListView(ObjectListView):
    queryset = NinjaTemplate.objects.all()
    table = NinjaTemplateTable
    filterset = NinjaTemplateFilterSet
    filterset_form = NinjaTemplateFilterForm


class NinjaTemplateEditView(ObjectEditView):
    queryset = NinjaTemplate.objects.all()
    form = NinjaTemplateForm


class NinjaTemplateDeleteView(ObjectDeleteView):
    queryset = NinjaTemplate.objects.all()


class NinjaTemplateChangeLogView(ObjectChangeLogView):
    base_template = "ninja_template.html"


for model in get_target_model_object_types():

    view_name = f"Ninja{model.__name__}View"

    @register_model_view(model, name="ninjaview", path="ninja")
    class DynamicNinjaView(ObjectView):
        """
        Dynamic view for rendering Ninja templates for specific Netbox objects.
        This view is automatically created for each supported model type.
        """

        queryset = model.objects.all()
        tab = ViewTab(
            label="Ninja",
            weight=10000,
        )

        model_class: Type[models.Model] = model

        def _get_object_type(self) -> ObjectType:
            """Get the ObjectType for the current model."""
            # pylint: disable=protected-access
            app_label = self.model_class._meta.app_label
            model_name = self.model_class._meta.model_name
            logger.debug(
                "Getting ObjectType for model %s in app %s", model_name, app_label
            )
            return ObjectType.objects.get(model=model_name)

        def _render_template(
            self, request: HttpRequest, template_id: str, pk: Any, target_object
        ) -> HttpResponse:
            """Render a specific Ninja template for the object."""
            try:
                template_obj = NinjaTemplate.objects.get(pk=template_id)
                return render(
                    request,
                    "ninja_rendered.html",
                    {"ninja_template": template_obj, "target_object": target_object},
                )
            except ObjectDoesNotExist:
                messages.error(
                    request, f"Ninja Template with ID {template_id} not found"
                )
            except Exception as err:
                messages.error(request, f"Error rendering template: {err}")
                logger.exception("Error rendering template %s", template_id)

            # pylint: disable=protected-access
            app_label = self.model_class._meta.app_label
            model_name = self.model_class._meta.model_name
            return redirect(reverse(f"{app_label}:{model_name}", args=[pk]))

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
            object_type = self._get_object_type()
            ninja_templates = object_type.ninja_templates.all()

            target_object = self.model_class.objects.get(pk=pk)
            template_id = request.GET.get("template_id")
            if template_id:
                return self._render_template(request, template_id, pk, target_object)

            return render(
                request,
                "ninja_tab.html",
                {
                    "object": target_object,
                    "ninja_templates": ninja_templates,
                    "tab": self.tab,
                },
            )

    DynamicNinjaView.__name__ = view_name
