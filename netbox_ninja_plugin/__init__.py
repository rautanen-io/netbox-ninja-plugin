from importlib import metadata

from netbox.plugins import PluginConfig

__version__ = metadata.version(__name__)


class NinjaPluginConfig(PluginConfig):
    """Configuration for the Netbox Ninja plugin.

    This plugin makes it possible to create dynamic configuration files from NetBox data
    and generate SVG images.
    """

    name = "netbox_ninja_plugin"
    base_url = "ninja"
    verbose_name = "Netbox Ninja"
    description = "Dynamic configuration files and images from NetBox."
    version = __version__
    author = "rautanen.io"
    author_email = "veikko@rautanen.io"
    required_settings = []
    default_settings = {}


config = NinjaPluginConfig  # pylint: disable=invalid-name
