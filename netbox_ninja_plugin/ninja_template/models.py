from __future__ import annotations

import json
import logging
from typing import Any, Optional, Tuple, Union

from django.core.validators import RegexValidator
from django.db.models import (
    CASCADE,
    CharField,
    ForeignKey,
    ManyToManyField,
    TextField,
    UniqueConstraint,
)
from django.urls import reverse
from django.utils.safestring import SafeString, mark_safe
from jinja2 import TemplateError, TemplateSyntaxError, UndefinedError
from netbox.models import NetBoxModel
from netbox.plugins import get_plugin_config
from utilities.jinja2 import render_jinja2

from netbox_ninja_plugin import config
from netbox_ninja_plugin.ninja_template.choices import NinjaTemplateOutputTypeChoices
from netbox_ninja_plugin.ninja_template.logic import NinjaTemplateMixin

logger = logging.getLogger(__name__)


class NinjaTemplate(NinjaTemplateMixin, NetBoxModel):
    """A model representing a template that can be rendered for NetBox objects.

    This model stores templates that can be rendered for specific object types in NetBox.
    Templates can have text or draw.io output types and are rendered
    using Jinja2 templating engine.
    """

    name: CharField[str] = CharField(
        unique=True,
        max_length=64,
    )

    output_type: CharField[str] = CharField(
        choices=NinjaTemplateOutputTypeChoices,
        default="",
        max_length=32,
    )

    object_types = ManyToManyField(
        to="core.ObjectType",
        related_name="ninja_templates",
        blank=True,
        help_text=("The object type(s) to which this template applies."),
    )

    object_type_filters = ManyToManyField(
        to="core.ObjectType",
        related_name="object_type_filters",
        blank=True,
        help_text=(
            "For each Ninja tab, add dropdown filters based on the object types selected here."
        ),
    )

    string_filters = ManyToManyField(
        to="netbox_ninja_plugin.NinjaTemplateStringFilter",
        related_name="ninja_templates",
        blank=True,
        help_text=("String-based filters available for this Ninja template."),
    )

    code = TextField(blank=True)

    def get_output_type_color(self) -> Optional[str]:
        """Get the color associated with the template's output type.

        Returns:
            Optional[str]: The color code for the output type, or None if not found.
        """
        # pylint: disable=no-member
        return NinjaTemplateOutputTypeChoices.colors.get(self.output_type)

    def render(
        self, frontend=False, **context: Any
    ) -> Tuple[Union[str, SafeString], bool]:
        """Render the template with the given context.

        Args:
            frontend: use frontend (JavaScript) to render Draw.io images.
            **context: Additional context variables to use in template rendering.

        Returns:
            Tuple[Union[str, SafeString], bool]: The rendered template output. For draw.io templates,
                returns a safe HTML string. If rendering fails, returns an error message. Also boolean
                is returned. False means there was an error, True means no errors.

        Raises:
            TemplateSyntaxError: If there's a syntax error in the template
            UndefinedError: If a template variable is undefined
            TemplateError: For other template-related errors
            Exception: For unexpected errors during rendering
        """
        context = self.get_context(**context)

        try:
            output = render_jinja2(self.code, context)
            if self.output_type == NinjaTemplateOutputTypeChoices.JSON:

                try:
                    json.loads(output)
                except (json.JSONDecodeError, TypeError) as err:
                    return f"JSON validation error: {err}", False

            output = output.replace("\r\n", "\n")
            if self.output_type == NinjaTemplateOutputTypeChoices.DRAW_IO:
                if frontend:
                    return mark_safe(output), True

                api_params = get_plugin_config(
                    "netbox_ninja_plugin",
                    "drawio_export_api",
                    default=config.default_settings["drawio_export_api"],
                )
                if not api_params["enabled"]:
                    return "<error>draw.io export API is not enabled.</error>", False

                return mark_safe(self.drawio_export_api_client(output)), True
            return output, True

        except TemplateSyntaxError as err:
            error_msg = f"Template syntax error in '{self.name}': {str(err)}"
            logger.error(error_msg)
            return f"Template Error: {error_msg}", False

        except UndefinedError as err:
            error_msg = f"Undefined variable in template '{self.name}': {str(err)}"
            logger.error(error_msg)
            return f"Template Error: {error_msg}", False

        except TemplateError as err:
            error_msg = f"Template error in '{self.name}': {str(err)}"
            logger.error(error_msg)
            return f"Template Error: {error_msg}", False

        # pylint: disable=broad-exception-caught
        except Exception as err:
            error_msg = f"Unexpected error rendering template '{self.name}': {str(err)}"
            logger.exception(error_msg)
            return f"Error: {error_msg}", False

    def __str__(self) -> str:
        """String representation of the template.

        Returns:
            str: The template name and primary key.
        """
        return f"{self.name} ({self.pk})"

    def get_absolute_url(self) -> str:
        """Get the absolute URL for the template.

        Returns:
            str: The URL for viewing this template.
        """
        return reverse("plugins:netbox_ninja_plugin:ninjatemplate", args=[self.pk])

    class Meta:
        """Meta options for the NinjaTemplate model."""

        ordering = ["name"]
        verbose_name = "ninja template"
        verbose_name_plural = "ninja templates"


class NinjaTemplateStringFilter(NetBoxModel):
    name: CharField[str] = CharField(
        max_length=64,
    )
    key: CharField[str] = CharField(
        unique=True,
        max_length=64,
        validators=[
            RegexValidator(
                regex=r"^[A-Za-z0-9]+$",
                message="Key must contain only alphanumeric characters (A-Z, a-z, 0-9).",
            )
        ],
        help_text=(
            "Machine-readable key used when referencing this string filter. "
            "Only alphanumeric characters are allowed."
        ),
    )

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse(
            "plugins:netbox_ninja_plugin:ninjatemplatestringfilter", args=[self.pk]
        )

    class Meta:
        ordering = ["name"]
        verbose_name = "ninja template string filter"
        verbose_name_plural = "ninja template string filters"


class NinjaTemplateStringFilterOption(NetBoxModel):
    string_filter = ForeignKey(
        to="netbox_ninja_plugin.NinjaTemplateStringFilter",
        related_name="options",
        on_delete=CASCADE,
    )
    value: CharField[str] = CharField(
        max_length=255,
    )
    label: CharField[str] = CharField(
        max_length=255,
        blank=True,
    )

    def __str__(self) -> str:
        return self.label or self.value

    def get_absolute_url(self) -> str:
        return reverse(
            "plugins:netbox_ninja_plugin:ninjatemplatestringfilteroption",
            args=[self.pk],
        )

    class Meta:
        ordering = ["string_filter__name", "value"]
        verbose_name = "ninja template string filter option"
        verbose_name_plural = "ninja template string filter options"
        constraints = [
            UniqueConstraint(
                fields=["string_filter", "value"],
                name="unique_string_filter_option_value",
            )
        ]
