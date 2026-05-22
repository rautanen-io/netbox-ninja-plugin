from django.urls import include, path
from utilities.urls import get_model_urls

from netbox_ninja_plugin.ninja_template import views as template_views

urlpatterns = [
    path(
        "templates/",
        include(get_model_urls("netbox_ninja_plugin", "ninjatemplate", detail=False)),
    ),
    path(
        "templates/<int:pk>/",
        include(get_model_urls("netbox_ninja_plugin", "ninjatemplate")),
    ),
    path(
        "string-filters/",
        include(
            get_model_urls(
                "netbox_ninja_plugin", "ninjatemplatestringfilter", detail=False
            )
        ),
    ),
    path(
        "string-filters/<int:pk>/",
        include(get_model_urls("netbox_ninja_plugin", "ninjatemplatestringfilter")),
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
