from core.api.serializers import ObjectTypeSerializer
from core.models import ObjectType
from netbox.api.fields import SerializedPKRelatedField
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework.serializers import HyperlinkedIdentityField, PrimaryKeyRelatedField

from netbox_ninja_plugin.ninja_template.models import (
    NinjaTemplate,
    NinjaTemplateStringFilter,
    NinjaTemplateStringFilterOption,
)


class NinjaTemplateStringFilterSerializer(NetBoxModelSerializer):
    url = HyperlinkedIdentityField(
        view_name="plugins-api:netbox_ninja_plugin-api:ninjatemplatestringfilter-detail"
    )

    class Meta:
        model = NinjaTemplateStringFilter
        fields = "__all__"


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
    object_type_filters = SerializedPKRelatedField(
        queryset=ObjectType.objects.all(),
        serializer=ObjectTypeSerializer,
        required=False,
        many=True,
    )
    string_filters = SerializedPKRelatedField(
        queryset=NinjaTemplateStringFilter.objects.all(),
        serializer=NinjaTemplateStringFilterSerializer,
        required=False,
        many=True,
    )

    class Meta:
        model = NinjaTemplate
        fields = "__all__"


class NinjaTemplateStringFilterOptionSerializer(NetBoxModelSerializer):
    url = HyperlinkedIdentityField(
        view_name=(
            "plugins-api:netbox_ninja_plugin-api:ninjatemplatestringfilteroption-detail"
        )
    )
    string_filter = PrimaryKeyRelatedField(
        queryset=NinjaTemplateStringFilter.objects.all(),
    )

    class Meta:
        model = NinjaTemplateStringFilterOption
        fields = "__all__"
