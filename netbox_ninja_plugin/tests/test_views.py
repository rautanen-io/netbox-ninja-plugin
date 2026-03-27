# pylint: disable=missing-function-docstring
from core.models import ObjectType
from dcim.models import Site
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from users.models import ObjectPermission, User

from netbox_ninja_plugin.helpers import (
    get_filter_variable_name,
    get_filter_variable_prefix,
    get_jinja_model_object_types,
    get_string_filter_variable_name,
    replace_whitespace_with_underscores,
)
from netbox_ninja_plugin.ninja_template.models import (
    NinjaTemplate,
    NinjaTemplateStringFilter,
    NinjaTemplateStringFilterOption,
)
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

    def test_string_filter_add_with_options(self):
        response = self.client.post(
            reverse("plugins:netbox_ninja_plugin:ninjatemplatestringfilter_add"),
            data={
                "name": "Status",
                "key": "status",
                "options-TOTAL_FORMS": "2",
                "options-INITIAL_FORMS": "0",
                "options-MIN_NUM_FORMS": "0",
                "options-MAX_NUM_FORMS": "1000",
                "options-0-value": "active",
                "options-0-label": "Active",
                "options-1-value": "planned",
                "options-1-label": "Planned",
            },
        )
        self.assertEqual(response.status_code, 302)
        created_filter = NinjaTemplateStringFilter.objects.get(key="status")
        self.assertEqual(created_filter.options.count(), 2)

    def test_string_filter_add_rejects_non_alphanumeric_key(self):
        response = self.client.post(
            reverse("plugins:netbox_ninja_plugin:ninjatemplatestringfilter_add"),
            data={
                "name": "Invalid Status",
                "key": "status filter!",
                "options-TOTAL_FORMS": "0",
                "options-INITIAL_FORMS": "0",
                "options-MIN_NUM_FORMS": "0",
                "options-MAX_NUM_FORMS": "1000",
            },
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertContains(
            response,
            "Key must contain only alphanumeric characters (A-Z, a-z, 0-9).",
        )
        self.assertFalse(
            NinjaTemplateStringFilter.objects.filter(name="Invalid Status").exists()
        )

    def test_ninja_template_string_filters_render_and_persist(self):
        site = Site.objects.create(name="site1")
        site_ot = ObjectType.objects.get(model="site")
        device_type_ot = ObjectType.objects.get(model="devicetype")
        object_filter_variable = get_filter_variable_name(device_type_ot)
        string_filter_variable = get_string_filter_variable_name("status")
        string_filter = NinjaTemplateStringFilter.objects.create(
            name="Status",
            key="status",
        )
        NinjaTemplateStringFilterOption.objects.create(
            string_filter=string_filter,
            value="active",
            label="Active",
        )
        NinjaTemplateStringFilterOption.objects.create(
            string_filter=string_filter,
            value="planned",
            label="Planned",
        )

        template = NinjaTemplate.objects.create(
            name="test",
            output_type="text",
            code=(
                f"ObjectFilterCount={{{{ {object_filter_variable}|length }}}}; "
                f"StatusCount={{{{ {string_filter_variable}|length }}}}"
            ),
        )
        template.object_types.add(site_ot)
        template.object_type_filters.add(device_type_ot)
        template.string_filters.add(string_filter)

        status_query_key = f"t{template.pk}__{string_filter_variable}"
        url = f"{site.get_absolute_url()}ninja/?{status_query_key}=active"
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertContains(response, "Filters (1)")
        self.assertContains(response, f'name="{status_query_key}"')
        self.assertContains(response, 'option value="active"')
        rendered_template = response.context["ninja_templates"][0]
        # Ninja tab now renders `NinjaTemplateCard` objects (wrapper with precomputed data).
        self.assertEqual(rendered_template.template.pk, template.pk)
        self.assertEqual(
            rendered_template.filter_values[string_filter_variable], ["active"]
        )
        self.assertIsNone(rendered_template.filter_values[object_filter_variable])

    def test_ninja_tab_invalid_target_pk_returns_404(self):
        site = Site.objects.create(name="site1", slug="site1")
        base_url = site.get_absolute_url()

        invalid_pk = site.pk + 9999
        # NetBox usually uses `<pk>-<slug>` in the final URL segment, but fall back to `<pk>/` if needed.
        invalid_url = base_url.replace(f"{site.pk}-", f"{invalid_pk}-", 1)
        if invalid_url == base_url:
            invalid_url = base_url.replace(f"/{site.pk}/", f"/{invalid_pk}/", 1)
        self.assertNotEqual(
            invalid_url,
            base_url,
            "Test URL rewrite failed; base URL format unexpected for Site.get_absolute_url().",
        )

        response = self.client.get(f"{invalid_url}ninja/")
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_ninja_tab_reset_scopes_to_template(self):
        site = Site.objects.create(name="site1")
        site_ot = ObjectType.objects.get(model="site")

        string_filter_variable = get_string_filter_variable_name("status")
        string_filter = NinjaTemplateStringFilter.objects.create(
            name="Status",
            key="status",
        )
        NinjaTemplateStringFilterOption.objects.create(
            string_filter=string_filter,
            value="active",
            label="Active",
        )
        NinjaTemplateStringFilterOption.objects.create(
            string_filter=string_filter,
            value="planned",
            label="Planned",
        )

        template_a = NinjaTemplate.objects.create(
            name="template-a",
            output_type="text",
            code=f"StatusCount={{{{ {string_filter_variable}|length }}}}",
        )
        template_b = NinjaTemplate.objects.create(
            name="template-b",
            output_type="text",
            code=f"StatusCount={{{{ {string_filter_variable}|length }}}}",
        )
        template_a.object_types.add(site_ot)
        template_b.object_types.add(site_ot)
        template_a.string_filters.add(string_filter)
        template_b.string_filters.add(string_filter)

        status_query_key_a = f"t{template_a.pk}__{string_filter_variable}"
        status_query_key_b = f"t{template_b.pk}__{string_filter_variable}"

        # Both templates have active filters on the same Ninja page.
        url = (
            f"{site.get_absolute_url()}ninja/"
            f"?{status_query_key_a}=active&{status_query_key_b}=planned"
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTP_200_OK)

        html = response.content.decode("utf-8")

        start_a = html.index(f'id="reset-filters-{template_a.pk}"')
        end_a = html.index("</form>", start_a) + len("</form>")
        reset_a_segment = html[start_a:end_a]

        self.assertNotIn(f'name="{status_query_key_a}"', reset_a_segment)
        self.assertIn(f'name="{status_query_key_b}"', reset_a_segment)

        start_b = html.index(f'id="reset-filters-{template_b.pk}"')
        end_b = html.index("</form>", start_b) + len("</form>")
        reset_b_segment = html[start_b:end_b]

        self.assertNotIn(f'name="{status_query_key_b}"', reset_b_segment)
        self.assertIn(f'name="{status_query_key_a}"', reset_b_segment)

    def test_ninja_tab_object_filter_respects_view_permissions(self):
        """Users cannot smuggle PKs for objects they are not allowed to view."""
        site_allowed = Site.objects.create(name="allowed-site", slug="allowed-site")
        site_other = Site.objects.create(name="other-site", slug="other-site")
        site_ot = ObjectType.objects.get(model="site")
        object_filter_variable = get_filter_variable_name(site_ot)
        template = NinjaTemplate.objects.create(
            name="perm test",
            output_type="text",
            code=f"FilterCount={{{{ {object_filter_variable}|length }}}}",
        )
        template.object_types.add(site_ot)
        template.object_type_filters.add(site_ot)

        obj_perm = ObjectPermission.objects.create(
            name="view constrained sites",
            enabled=True,
            actions=["view"],
            constraints={"pk": site_allowed.pk},
        )
        obj_perm.object_types.add(ContentType.objects.get_for_model(Site))
        limited_user = User.objects.create_user(
            username="limited",
            email="limited@example.com",
            password="limited",
        )
        obj_perm.users.add(limited_user)

        query_key = f"t{template.pk}__{object_filter_variable}"
        url = f"{site_allowed.get_absolute_url()}ninja/?{query_key}={site_other.pk}"
        self.client.login(username="limited", password="limited")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        rendered = response.context["ninja_templates"][0]
        self.assertIsNone(rendered.filter_values[object_filter_variable])

    def test_ninjatemplate_string_filter_dropdown_renders_and_applies(self):
        string_filter_variable = get_string_filter_variable_name("status")

        string_filter = NinjaTemplateStringFilter.objects.create(
            name="Status",
            key="status",
        )
        NinjaTemplateStringFilterOption.objects.create(
            string_filter=string_filter,
            value="active",
            label="Active",
        )
        NinjaTemplateStringFilterOption.objects.create(
            string_filter=string_filter,
            value="planned",
            label="Planned",
        )

        template = NinjaTemplate.objects.create(
            name="test",
            output_type="text",
            code=f"StatusCount={{{{ {string_filter_variable}|length }}}}",
        )
        # Keep `object_types` empty so the page renders the "Rendered" preview branch.
        template.string_filters.add(string_filter)

        query_key = f"t{template.pk}__{string_filter_variable}"
        url = f"{template.get_absolute_url()}?{query_key}=active"
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertContains(response, "Filters (1)")
        self.assertContains(response, f'name="{query_key}"')
        self.assertContains(response, 'option value="active"')

        rendered_card = response.context["ninja_template_card"]
        self.assertEqual(
            rendered_card.filter_values[string_filter_variable],
            ["active"],
        )
        self.assertContains(response, "StatusCount=1")

    def test_ninjatemplate_drawio_filters_are_applied_in_viewer_script(self):
        string_filter_variable = get_string_filter_variable_name("status")

        string_filter = NinjaTemplateStringFilter.objects.create(
            name="Status",
            key="status",
        )
        NinjaTemplateStringFilterOption.objects.create(
            string_filter=string_filter,
            value="active",
            label="Active",
        )

        template = NinjaTemplate.objects.create(
            name="test-drawio",
            output_type="drawio",
            code=f"StatusLen={{{{ {string_filter_variable}|length }}}}",
        )
        template.string_filters.add(string_filter)

        query_key = f"t{template.pk}__{string_filter_variable}"
        url = f"{template.get_absolute_url()}?{query_key}=active"
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertContains(response, f'name="{query_key}"')
        # `_drawio_script.html` wraps render output in `{% filter escapejs %}`,
        # which escapes `=` as `\u003D`.
        self.assertContains(response, "StatusLen\\u003D1")
        self.assertIn(
            f"return_url={template.get_absolute_url()}",
            response.content.decode("utf-8"),
        )

    def test_jinja_model_querysets_keys_are_case_sensitive(self):
        """
        Jinja variable lookups are case sensitive.

        Ensure queryset variable keys in template context preserve the original
        casing from NetBox `verbose_name_plural` (so users must use e.g.
        `IP_addresses`, not `ip_addresses`).
        """
        jinja_models = get_jinja_model_object_types()
        # Pick a configured model where verbose_name_plural includes uppercase
        # characters, so we can validate case sensitivity.
        selected_model = next(
            (
                m
                for m in jinja_models
                if any(c.isupper() for c in str(m._meta.verbose_name_plural))
            ),
            None,
        )
        if selected_model is None:
            self.skipTest(
                "No configured jinja model has uppercase in verbose_name_plural."
            )

        orig_key = replace_whitespace_with_underscores(
            str(selected_model._meta.verbose_name_plural)
        )
        lower_key = orig_key.lower()

        template = NinjaTemplate.objects.create(
            name="jinja-key-test",
            output_type="text",
            code=f"OrigLen={{{{ {orig_key}|length }}}}",
        )
        context = template.get_context()

        self.assertIn(orig_key, context)
        self.assertNotIn(lower_key, context)

        # Also ensure `filter_*` variables preserve the same casing.
        selected_ot = ObjectType.objects.get(
            app_label=selected_model._meta.app_label,
            model=selected_model._meta.model_name,
        )
        expected_filter_var = f"{get_filter_variable_prefix()}{orig_key}"
        self.assertEqual(get_filter_variable_name(selected_ot), expected_filter_var)
