from core.models import ObjectType
from extras.api.serializers import ObjectTypeSerializer
from netbox.api.fields import SerializedPKRelatedField
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework.serializers import HyperlinkedIdentityField

from netbox_ninja_plugin.ninja_template.models import NinjaTemplate


class NinjaTemplateSerializer(NetBoxModelSerializer):
    url = HyperlinkedIdentityField(
        view_name="plugins-api:netbox_ninja_plugin-api:ninjatemplate-detail"
    )

    object_types = SerializedPKRelatedField(
        queryset=ObjectType.objects.all(),
        serializer=ObjectTypeSerializer,
        required=False,
        many=True,
    )

    class Meta:
        model = NinjaTemplate
        fields = "__all__"
