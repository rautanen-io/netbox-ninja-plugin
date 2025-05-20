# pylint: disable=missing-function-docstring
from core.models import ObjectType
from dcim.models import Site
from rest_framework.status import HTTP_200_OK

from netbox_ninja_plugin.ninja_template.models import NinjaTemplate
from netbox_ninja_plugin.tests import TestNinjaTemplateMixing


class TestNinjaTemplateViews(TestNinjaTemplateMixing):

    def test_ninja_template_list_view(self):
        response = self.get("ninjatemplate_list")
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_ninja_template_view(self):
        template = NinjaTemplate.objects.create(name="test")
        response = self.get("ninjatemplate", template.pk)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_ninja_template_add(self):
        response = self.get("ninjatemplate_add")
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_ninja_template_edit(self):
        template = NinjaTemplate.objects.create(name="test")
        response = self.get("ninjatemplate_edit", template.pk)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_ninja_template_changelog(self):
        template = NinjaTemplate.objects.create(name="test")
        response = self.get("ninjatemplate_changelog", template.pk)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_ninja_template_render(self):
        template = NinjaTemplate.objects.create(
            name="test", code="""Name of this template: {{ target_object.name }}"""
        )
        url = f"/api{template.get_absolute_url()}render/?app=netbox_ninja_plugin&model=ninjatemplate&pk={template.pk}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.content, b"Name of this template: test")

    def test_ninja_template_target_object_render(self):
        site = Site.objects.create(name="site1")
        site_ot = ObjectType.objects.get(model="site")
        template = NinjaTemplate.objects.create(
            name="test",
            output_type="text",
            code="""Name of this object: {{ target_object.name }}""",
        )
        template.object_types.add(site_ot)
        template.save()

        url = f"{site.get_absolute_url()}ninja/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("Name of this object: site1", str(response.content))

        url = f"{site.get_absolute_url()}ninja/?template_id={template.pk}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("Name of this object: site1", str(response.content))
