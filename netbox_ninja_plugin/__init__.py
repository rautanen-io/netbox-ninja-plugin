from importlib import metadata

from netbox.plugins import PluginConfig

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
    min_version = "4.2.3"
    max_version = "4.3.7"
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
        "top_level_menu": False,
    }


config = NinjaPluginConfig  # pylint: disable=invalid-name
