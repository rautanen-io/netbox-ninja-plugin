import logging
from typing import Any, Type

from core.models import ObjectType
from django.db import models
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
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


for model in get_target_model_object_types():
    _register_ninja_tab_view(model)
