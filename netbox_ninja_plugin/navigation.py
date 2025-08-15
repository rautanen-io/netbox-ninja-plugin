from netbox.plugins import (
    PluginMenu,
    PluginMenuButton,
    PluginMenuItem,
    get_plugin_config,
)

_menu_items = (
    PluginMenuItem(
        link="plugins:netbox_ninja_plugin:ninjatemplate_list",
        link_text="Templates",
        permissions=["netbox_ninja_plugin.view_ninjatemplate"],
        buttons=[
            PluginMenuButton(
                link="plugins:netbox_ninja_plugin:ninjatemplate_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=["netbox_ninja_plugin.add_ninjatemplate"],
            )
        ],
    ),
)


if get_plugin_config(
    "netbox_ninja_plugin",
    "top_level_menu",
    default=False,
):
    menu = PluginMenu(
        label="Ninja",
        groups=(
            (
                "Ninja",
                _menu_items,
            ),
        ),
        icon_class="mdi mdi-ninja",
    )
else:
    menu_items = _menu_items
