from core.models import ObjectType
from django.core.exceptions import ValidationError
from django.forms import (
    BaseInlineFormSet,
    CharField,
    ChoiceField,
    ModelForm,
    ModelMultipleChoiceField,
    Textarea,
    inlineformset_factory,
)
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms import add_blank_choice
from utilities.forms.fields import ContentTypeMultipleChoiceField, TagFilterField
from utilities.forms.rendering import FieldSet

from netbox_ninja_plugin.helpers import (
    get_filter_variable_prefix,
    get_jinja_model_names,
    get_jinja_model_plural_names,
    get_model_names,
)
from netbox_ninja_plugin.ninja_template.choices import NinjaTemplateOutputTypeChoices
from netbox_ninja_plugin.ninja_template.models import (
    NinjaTemplate,
    NinjaTemplateStringFilter,
    NinjaTemplateStringFilterOption,
)


class NinjaTemplateForm(NetBoxModelForm):

    object_types = ContentTypeMultipleChoiceField(
        required=False,
        label=("Object types"),
        queryset=ObjectType.objects.filter(model__in=get_model_names()),
        help_text="Select the Netbox models having this template.",
    )
    object_type_filters = ContentTypeMultipleChoiceField(
        required=False,
        label=("Object type filters"),
        queryset=ObjectType.objects.filter(model__in=get_jinja_model_names()),
        help_text=(
            "Add dropdown filters to Ninja tabs using objects from these model types."
        ),
    )
    string_filters = ModelMultipleChoiceField(
        required=False,
        label=("String filters"),
        queryset=NinjaTemplateStringFilter.objects.all(),
        help_text="Attach reusable string-based filters to this template.",
    )
    # Display the machine-readable key in the UI instead of the human name.
    string_filters.label_from_instance = lambda obj: f"{obj.name} ({obj.key})"

    code = CharField(
        required=False,
        label="Code",
        widget=Textarea(attrs={"cols": "40", "rows": "20"}),
        help_text=(
            f"""Supported querysets: {
                ', '.join([f'{{{{ {name} }}}}' for name in get_jinja_model_plural_names()])
            }.
            Use {{{{ target_object }}}} for the current NetBox object instance.
            Object Type and string filters are exposed as Jinja variables using the configured
            "filter_variable_prefix" (currently "{get_filter_variable_prefix()}", e.g.
            {{{{ {get_filter_variable_prefix()}sites }}}})."""
        ),
    )

    fieldsets = [
        FieldSet(
            "name",
            "output_type",
            "object_types",
            "object_type_filters",
            "string_filters",
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
            "object_type_filters",
            "string_filters",
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
        queryset=ObjectType.objects.filter(model__in=get_model_names()),
    )
    object_type_filters = ContentTypeMultipleChoiceField(
        required=False,
        queryset=ObjectType.objects.filter(model__in=get_jinja_model_names()),
    )
    string_filters = ModelMultipleChoiceField(
        required=False,
        queryset=NinjaTemplateStringFilter.objects.all(),
    )
    # Display the machine-readable key in the UI instead of the human name.
    string_filters.label_from_instance = lambda obj: f"{obj.name} ({obj.key})"

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
            "object_type_filters",
            "string_filters",
            "code",
            name="Template",
        ),
    ]


class NinjaTemplateStringFilterForm(NetBoxModelForm):
    class Meta:
        model = NinjaTemplateStringFilter
        fields = [
            "name",
            "key",
            "tags",
        ]


class NinjaTemplateStringFilterFilterForm(NetBoxModelFilterSetForm):
    model = NinjaTemplateStringFilter

    tag = TagFilterField(model)

    name = CharField(
        required=False,
    )
    key = CharField(
        required=False,
    )

    fieldsets = [
        FieldSet(
            "q",
            "filter_id",
            "tag",
        ),
        FieldSet(
            "name",
            "key",
            name="String Filter",
        ),
    ]


class NinjaTemplateStringFilterOptionForm(NetBoxModelForm):
    class Meta:
        model = NinjaTemplateStringFilterOption
        fields = [
            "string_filter",
            "value",
            "label",
            "tags",
        ]


class NinjaTemplateStringFilterOptionInlineForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "tags" in self.fields:
            self.fields["tags"].required = False

    class Meta:
        model = NinjaTemplateStringFilterOption
        fields = [
            "value",
            "label",
            "tags",
        ]


class NinjaTemplateStringFilterOptionInlineFormSet(BaseInlineFormSet):
    def clean(self):
        # Before super(): BaseModelFormSet.clean() calls validate_unique(), which
        # reports duplicates with Django's generic message if super() runs first.
        seen_values = set()
        for form in self.forms:
            if not hasattr(form, "cleaned_data") or not form.cleaned_data:
                continue
            if form.cleaned_data.get("DELETE", False):
                continue

            value = (form.cleaned_data.get("value") or "").strip()
            if not value:
                continue

            if value in seen_values:
                raise ValidationError(
                    "Option values must be unique within a string filter."
                )
            seen_values.add(value)

        super().clean()


NinjaTemplateStringFilterOptionFormSet = inlineformset_factory(
    NinjaTemplateStringFilter,
    NinjaTemplateStringFilterOption,
    form=NinjaTemplateStringFilterOptionInlineForm,
    formset=NinjaTemplateStringFilterOptionInlineFormSet,
    extra=1,
    can_delete=True,
)


class NinjaTemplateStringFilterOptionFilterForm(NetBoxModelFilterSetForm):
    model = NinjaTemplateStringFilterOption

    tag = TagFilterField(model)

    value = CharField(
        required=False,
    )
    label = CharField(
        required=False,
    )

    fieldsets = [
        FieldSet(
            "q",
            "filter_id",
            "tag",
        ),
        FieldSet(
            "string_filter",
            "value",
            "label",
            name="String Filter Option",
        ),
    ]
