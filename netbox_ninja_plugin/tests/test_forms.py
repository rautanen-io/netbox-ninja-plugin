# pylint: disable=missing-function-docstring
from core.models import ObjectType

from netbox_ninja_plugin.ninja_template.choices import NinjaTemplateOutputTypeChoices
from netbox_ninja_plugin.ninja_template.forms import NinjaTemplateForm
from netbox_ninja_plugin.tests import TestNinjaTemplateMixing


class TestNinjaTemplateForm(TestNinjaTemplateMixing):

    def test_ninja_template_submit_form(self):
        interface_ot = ObjectType.objects.get(model="interface")

        form_input = {
            "name": None,
            "object_types": None,
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
            "output_type": NinjaTemplateOutputTypeChoices.DRAW_IO,
            "code": None,
        }
        form = NinjaTemplateForm(data=form_input)
        self.assertEqual(len(form.errors), 0)

        form_input = {
            "name": "test",
            "object_types": [interface_ot],
            "output_type": NinjaTemplateOutputTypeChoices.TEXT,
            "code": "some code",
        }
        form = NinjaTemplateForm(data=form_input)
        self.assertEqual(len(form.errors), 0)
