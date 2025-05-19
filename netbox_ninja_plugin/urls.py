from django.urls import include, path
from utilities.urls import get_model_urls

from netbox_ninja_plugin.ninja_template import views as template_views

urlpatterns = [
    path(
        "templates/",
        template_views.NinjaTemplateListView.as_view(),
        name="ninjatemplate_list",
    ),
    path(
        "templates/<int:pk>/",
        include(get_model_urls("netbox_ninja_plugin", "ninjatemplate")),
    ),
    path(
        "templates/add/",
        template_views.NinjaTemplateEditView.as_view(),
        name="ninjatemplate_add",
    ),
]
