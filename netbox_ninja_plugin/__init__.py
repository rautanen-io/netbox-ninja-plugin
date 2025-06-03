from importlib import metadata

from netbox.plugins import (
    PluginConfig,
    register_menu_items,
    register_template_extensions,
)

__version__ = metadata.version(__name__)


class NinjaPluginConfig(PluginConfig):
    """Configuration for the Netbox Ninja plugin.

    This plugin makes it possible to create dynamic configuration files from NetBox data and generate SVG images.
    """

    name = "netbox_ninja_plugin"
    base_url = "ninja"
    verbose_name = "Netbox Ninja"
    description = "Dynamic configuration files and images from NetBox."
    version = __version__
    min_version = "4.0.11"
    max_version = "4.2.7"
    author = "rautanen.io"
    author_email = "veikko@rautanenyhtiot.fi"
    required_settings = []
    default_settings = {
        "target_models": {
            "dcim": ["device", "interface", "site", "region"],
            "ipam": ["prefix"],
        },
        "jinja_model_querysets": {
            "dcim": ["device", "interface", "site", "region"],
            "ipam": ["prefix"],
        },
        "drawio_export_api": {
            "enabled": False,
            "url": "https://drawio-export-api:443/svg",
            "token": "token1",
            "pem_file_path": "/opt/netbox_ninja_plugin/develop/fullchain.pem",
            "verify_tls": True,
            "timeout": 60,
        },
    }

    # pylint: disable=import-outside-toplevel,unused-import
    def ready(self) -> None:
        """Initialize the plugin when it's loaded.

        This method is called when the plugin is loaded. It registers the template
        extensions and menu items.
        """
        from netbox_ninja_plugin.navigation import plugin_navigation
        from netbox_ninja_plugin.template_content import template_extensions

        register_template_extensions(template_extensions)

        for title, items in plugin_navigation.items():
            register_menu_items(title, items)


config = NinjaPluginConfig  # pylint: disable=invalid-name
