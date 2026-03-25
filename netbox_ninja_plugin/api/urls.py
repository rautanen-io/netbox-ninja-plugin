from django.urls import include, path
from netbox.api.routers import NetBoxRouter

from netbox_ninja_plugin.api.views import (
    NinjaRenderView,
    NinjaTemplateStringFilterOptionViewSet,
    NinjaTemplateStringFilterViewSet,
    NinjaTemplateViewSet,
)

router = NetBoxRouter()
router.register("templates", NinjaTemplateViewSet)
router.register("string-filters", NinjaTemplateStringFilterViewSet)
router.register("string-filter-options", NinjaTemplateStringFilterOptionViewSet)

app_name = "netbox_ninja_plugin"
urlpatterns = router.urls

urlpatterns = [
    path("", include(router.urls)),
    path(
        "templates/<int:pk>/render/",
        NinjaRenderView.as_view(),
        name="ninjatemplate-render",
    ),
]
