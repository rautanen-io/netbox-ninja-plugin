from django_tables2 import A, Column
from netbox.tables import NetBoxTable
from netbox.tables.columns import ChoiceFieldColumn, ContentTypesColumn, TagColumn

from netbox_ninja_plugin.ninja_template.models import NinjaTemplate


class NinjaTemplateTable(NetBoxTable):

    _name = Column(accessor=A("name"), linkify=True)
    object_types = ContentTypesColumn(verbose_name="Object Types")
    output_type = ChoiceFieldColumn()
    tags = TagColumn()

    class Meta(NetBoxTable.Meta):
        model = NinjaTemplate
        fields = ("_name",)
        default_columns = ("_name", "object_types", "output_type", "tags")
