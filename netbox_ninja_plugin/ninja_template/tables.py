from django_tables2 import A, Column, ManyToManyColumn
from netbox.tables import NetBoxTable
from netbox.tables.columns import ChoiceFieldColumn, ContentTypesColumn, TagColumn

from netbox_ninja_plugin.ninja_template.models import (
    NinjaTemplate,
    NinjaTemplateStringFilter,
    NinjaTemplateStringFilterOption,
)


class NinjaTemplateTable(NetBoxTable):

    _name = Column(accessor=A("name"), linkify=True)
    object_types = ContentTypesColumn(verbose_name="Object Types")
    object_type_filters = ContentTypesColumn(verbose_name="Object Type Filters")
    string_filters = ManyToManyColumn(verbose_name="String Filters")
    output_type = ChoiceFieldColumn()
    tags = TagColumn()

    class Meta(NetBoxTable.Meta):
        model = NinjaTemplate
        fields = ("_name",)
        default_columns = (
            "_name",
            "object_types",
            "output_type",
            "tags",
        )


class NinjaTemplateStringFilterTable(NetBoxTable):
    _name = Column(accessor=A("name"), linkify=True)
    options_count = Column(accessor=A("options.count"), verbose_name="Options")
    tags = TagColumn()

    class Meta(NetBoxTable.Meta):
        model = NinjaTemplateStringFilter
        fields = ("_name", "key", "options_count", "tags")
        default_columns = (
            "_name",
            "key",
            "options_count",
            "tags",
        )


class NinjaTemplateStringFilterOptionTable(NetBoxTable):
    _value = Column(accessor=A("value"), linkify=True, verbose_name="Value")
    tags = TagColumn()

    class Meta(NetBoxTable.Meta):
        model = NinjaTemplateStringFilterOption
        fields = ("_value", "label", "string_filter", "tags")
        default_columns = (
            "_value",
            "label",
            "string_filter",
            "tags",
        )
