from django.urls import include, path
from netbox.api.routers import NetBoxRouter

from netbox_ninja_plugin.api.views import NinjaTemplateViewSet

router = NetBoxRouter()
router.register("templates", NinjaTemplateViewSet)

app_name = "netbox_ninja_plugin"
urlpatterns = router.urls

urlpatterns = [
    path("", include(router.urls)),
]
