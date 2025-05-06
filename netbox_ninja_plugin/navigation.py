from netbox.plugins import PluginMenuButton, PluginMenuItem

plugin_navigation = {
    "Ninja": [
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
    ],
}
