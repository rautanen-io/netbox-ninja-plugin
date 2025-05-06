from netbox.api.viewsets import NetBoxModelViewSet

from netbox_ninja_plugin.api.serializers import NinjaTemplateSerializer
from netbox_ninja_plugin.ninja_template.models import NinjaTemplate


class NinjaTemplateViewSet(NetBoxModelViewSet):
    queryset = NinjaTemplate.objects.all()
    serializer_class = NinjaTemplateSerializer
