from core.models import ObjectType
from netbox.plugins import PluginTemplateExtension

from netbox_ninja_plugin.helpers import get_target_model_fully_qualified_names

template_extensions = []

for target_model in get_target_model_fully_qualified_names():
    # pylint: disable=abstract-method
    class NinjaPluginCard(PluginTemplateExtension):
        """A template extension that adds a card to the right side of object detail pages.

        This card displays Ninja templates related to the current object. The card is added
        to all pages of models specified in the plugin configuration.
        """

        # Using model and not models to support older Netbox versions.
        model = target_model

        def right_page(self) -> str:
            """Render the right page card for the current object.

            Returns:
                str: Rendered HTML content for the card showing available Ninja templates
                    for the current object.
            """
            # pylint: disable=protected-access
            model = self.context["object"]._meta.model_name

            object_type = ObjectType.objects.get(model=model)
            return self.render(
                "ninja_object_card.html",
                {
                    "card_header": "Ninja templates",
                    "object_type": object_type,
                },
            )

    NinjaPluginCard.__name__ = (
        "NinjaPluginCard"
        + f"{''.join(part.capitalize() for part in target_model.strip().split('.'))}"
    )

    template_extensions.append(NinjaPluginCard)
