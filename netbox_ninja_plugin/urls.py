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
    path(
        "string-filters/",
        template_views.NinjaTemplateStringFilterListView.as_view(),
        name="ninjatemplatestringfilter_list",
    ),
    path(
        "string-filters/<int:pk>/",
        include(get_model_urls("netbox_ninja_plugin", "ninjatemplatestringfilter")),
    ),
    path(
        "string-filters/add/",
        template_views.NinjaTemplateStringFilterEditView.as_view(),
        name="ninjatemplatestringfilter_add",
    ),
    path(
        "string-filter-options/",
        template_views.NinjaTemplateStringFilterOptionListView.as_view(),
        name="ninjatemplatestringfilteroption_list",
    ),
    path(
        "string-filter-options/<int:pk>/",
        include(
            get_model_urls("netbox_ninja_plugin", "ninjatemplatestringfilteroption")
        ),
    ),
    path(
        "string-filter-options/add/",
        template_views.NinjaTemplateStringFilterOptionEditView.as_view(),
        name="ninjatemplatestringfilteroption_add",
    ),
]
