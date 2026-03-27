# pylint: disable=missing-function-docstring
from core.models import ObjectType

from netbox_ninja_plugin.helpers import get_jinja_model_names
from netbox_ninja_plugin.ninja_template.choices import NinjaTemplateOutputTypeChoices
from netbox_ninja_plugin.ninja_template.forms import (
    NinjaTemplateFilterForm,
    NinjaTemplateForm,
    NinjaTemplateStringFilterOptionFormSet,
)
from netbox_ninja_plugin.ninja_template.models import NinjaTemplateStringFilter
from netbox_ninja_plugin.tests import TestNinjaTemplateMixing


class TestNinjaTemplateForm(TestNinjaTemplateMixing):

    def test_ninja_template_submit_form(self):
        form_input = {
            "name": None,
            "object_types": None,
            "object_type_filters": None,
            "output_type": None,
            "code": None,
        }
        form = NinjaTemplateForm(data=form_input)
        self.assertEqual(len(form.errors), 2)
        self.assertDictEqual(
            form.errors,
            {
                "name": ["This field is required."],
                "output_type": ["This field is required."],
            },
        )
        form_input = {
            "name": "test",
            "object_types": None,
            "object_type_filters": None,
            "output_type": "problem",
            "code": None,
        }
        form = NinjaTemplateForm(data=form_input)
        self.assertEqual(len(form.errors), 1)
        self.assertDictEqual(
            form.errors,
            {
                "output_type": [
                    "Select a valid choice. problem is not one of the available choices."
                ]
            },
        )

        form_input = {
            "name": "test",
            "object_types": None,
            "object_type_filters": None,
            "output_type": NinjaTemplateOutputTypeChoices.DRAW_IO,
            "code": None,
        }
        form = NinjaTemplateForm(data=form_input)
        self.assertEqual(len(form.errors), 0)


class TestNinjaTemplateStringFilterOptionFormSet(TestNinjaTemplateMixing):
    def test_duplicate_values_rejected(self):
        string_filter = NinjaTemplateStringFilter.objects.create(
            name="Status",
            key="status",
        )
        formset = NinjaTemplateStringFilterOptionFormSet(
            data={
                "options-TOTAL_FORMS": "2",
                "options-INITIAL_FORMS": "0",
                "options-MIN_NUM_FORMS": "0",
                "options-MAX_NUM_FORMS": "1000",
                "options-0-value": "active",
                "options-0-label": "Active",
                "options-1-value": "active",
                "options-1-label": "Active duplicate",
            },
            instance=string_filter,
            prefix="options",
        )
        self.assertFalse(formset.is_valid())
        self.assertIn(
            "Option values must be unique within a string filter.",
            formset.non_form_errors(),
        )

    def test_object_type_filters_queryset_uses_jinja_object_types(self):

        interface_ot = ObjectType.objects.get(model="interface")
        site_ot = ObjectType.objects.get(model="site")

        create_form = NinjaTemplateForm()
        filter_form = NinjaTemplateFilterForm()

        self.assertQuerySetEqual(
            create_form.fields["object_type_filters"].queryset.order_by("pk"),
            ObjectType.objects.filter(model__in=get_jinja_model_names()).order_by("pk"),
            transform=lambda obj: obj,
        )
        self.assertQuerySetEqual(
            filter_form.fields["object_type_filters"].queryset.order_by("pk"),
            ObjectType.objects.filter(model__in=get_jinja_model_names()).order_by("pk"),
            transform=lambda obj: obj,
        )

        form_input = {
            "name": "test",
            "object_types": [interface_ot],
            "object_type_filters": [site_ot],
            "output_type": NinjaTemplateOutputTypeChoices.TEXT,
            "code": "some code",
        }
        form = NinjaTemplateForm(data=form_input)
        self.assertEqual(len(form.errors), 0)
