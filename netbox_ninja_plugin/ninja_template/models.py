from __future__ import annotations

import logging
from typing import Any, Optional, Union

from django.db.models import CharField, ManyToManyField, TextField
from django.urls import reverse
from django.utils.safestring import SafeString, mark_safe
from jinja2 import TemplateError, TemplateSyntaxError, UndefinedError
from netbox.models import NetBoxModel
from utilities.jinja2 import render_jinja2

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

    code = TextField(blank=True)

    def get_output_type_color(self) -> Optional[str]:
        """Get the color associated with the template's output type.

        Returns:
            Optional[str]: The color code for the output type, or None if not found.
        """
        # pylint: disable=no-member
        return NinjaTemplateOutputTypeChoices.colors.get(self.output_type)

    def render(self, **context: Any) -> Union[str, SafeString]:
        """Render the template with the given context.

        Args:
            **context: Additional context variables to use in template rendering.

        Returns:
            Union[str, SafeString]: The rendered template output. For draw.io templates,
                returns a safe HTML string. If rendering fails, returns an error message.

        Raises:
            TemplateSyntaxError: If there's a syntax error in the template
            UndefinedError: If a template variable is undefined
            TemplateError: For other template-related errors
            Exception: For unexpected errors during rendering
        """
        context = self.get_context(**context)

        try:
            output = render_jinja2(self.code, context)
            output = output.replace("\r\n", "\n")
            if self.output_type == NinjaTemplateOutputTypeChoices.DRAW_IO:
                return mark_safe(self.drawio_export_api_client(output))
            return output

        except TemplateSyntaxError as err:
            error_msg = f"Template syntax error in '{self.name}': {str(err)}"
            logger.error(error_msg)
            return f"Template Error: {error_msg}"

        except UndefinedError as err:
            error_msg = f"Undefined variable in template '{self.name}': {str(err)}"
            logger.error(error_msg)
            return f"Template Error: {error_msg}"

        except TemplateError as err:
            error_msg = f"Template error in '{self.name}': {str(err)}"
            logger.error(error_msg)
            return f"Template Error: {error_msg}"

        # pylint: disable=broad-exception-caught
        except Exception as err:
            error_msg = f"Unexpected error rendering template '{self.name}': {str(err)}"
            logger.exception(error_msg)
            return f"Error: {error_msg}"

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
