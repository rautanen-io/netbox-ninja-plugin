from core.models import ObjectType
from django.forms import CharField, ChoiceField, Textarea
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms import add_blank_choice
from utilities.forms.fields import ContentTypeMultipleChoiceField, TagFilterField
from utilities.forms.rendering import FieldSet

from netbox_ninja_plugin.helpers import (
    get_jinja_model_plural_names,
    get_target_model_names,
)
from netbox_ninja_plugin.ninja_template.choices import NinjaTemplateOutputTypeChoices
from netbox_ninja_plugin.ninja_template.models import NinjaTemplate


class NinjaTemplateForm(NetBoxModelForm):

    object_types = ContentTypeMultipleChoiceField(
        required=False,
        label=("Object types"),
        queryset=ObjectType.objects.filter(model__in=get_target_model_names()),
        help_text="Select the Netbox models having this template.",
    )

    code = CharField(
        required=False,
        label="Code",
        widget=Textarea(attrs={"cols": "40", "rows": "20"}),
        help_text=(
            f"""Supported querysets: {
                ', '.join([f'{{{{ {name} }}}}' for name in get_jinja_model_plural_names()])
            }. If you selected Object Types, use {{{{ target_object }}}} to access to the Netbox
             model instance's data."""
        ),
    )

    fieldsets = [
        FieldSet(
            "name",
            "output_type",
            "object_types",
            "tags",
            "code",
            name="Template",
        ),
    ]

    class Meta:
        model = NinjaTemplate
        fields = [
            "name",
            "object_types",
            "output_type",
            "tags",
            "code",
        ]


class NinjaTemplateFilterForm(NetBoxModelFilterSetForm):
    model = NinjaTemplate

    tag = TagFilterField(model)

    name = CharField(
        required=False,
    )

    output_type = ChoiceField(
        choices=add_blank_choice(NinjaTemplateOutputTypeChoices),
        required=False,
    )

    object_types = ContentTypeMultipleChoiceField(
        required=False,
        queryset=ObjectType.objects.filter(model__in=get_target_model_names()),
    )

    fieldsets = [
        FieldSet(
            "q",
            "filter_id",
            "tag",
        ),
        FieldSet(
            "name",
            "output_type",
            "object_types",
            "code",
            name="Template",
        ),
    ]
