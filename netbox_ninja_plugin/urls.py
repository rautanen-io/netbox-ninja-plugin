from django.urls import path

from netbox_ninja_plugin.ninja_template import views as template_views
from netbox_ninja_plugin.ninja_template.models import NinjaTemplate

urlpatterns = [
    path(
        "templates/",
        template_views.NinjaTemplateListView.as_view(),
        name="ninjatemplate_list",
    ),
    path(
        "templates/<int:pk>/",
        template_views.NinjaTemplateView.as_view(),
        name="ninjatemplate",
    ),
    path(
        "templates/<int:pk>/render",
        template_views.NinjaTemplateRenderView.as_view(),
        name="ninjatemplate_render",
    ),
    path(
        "templates/add/",
        template_views.NinjaTemplateEditView.as_view(),
        name="ninjatemplate_add",
    ),
    path(
        "templates/<int:pk>/edit/",
        template_views.NinjaTemplateEditView.as_view(),
        name="ninjatemplate_edit",
    ),
    path(
        "templates/<int:pk>/delete/",
        template_views.NinjaTemplateDeleteView.as_view(),
        name="ninjatemplate_delete",
    ),
    path(
        "templates/<int:pk>/changelog/",
        template_views.NinjaTemplateChangeLogView.as_view(),
        name="ninjatemplate_changelog",
        kwargs={"model": NinjaTemplate},
    ),
]
