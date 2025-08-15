# Netbox Ninja Plugin Configuration

This document provides detailed information about the Netbox Ninja Plugin configuration options.

## Plugin Configuration

The plugin is configured through NetBox's `PLUGINS_CONFIG` setting. Here's a detailed explanation of each configuration option:

### Basic Configuration

```python
PLUGINS_CONFIG = {
    "netbox_ninja_plugin": {
        "target_models": {
            "dcim": ["device", "interface", "site", "region"],
            "ipam": ["prefix"],
        },
        "jinja_model_querysets": {
            "dcim": ["device", "interface", "site", "region"],
            "ipam": ["prefix"],
        },
        "drawio_export_api": {
            "enabled": True,
            "url": "https://drawio-export-api:443/svg",
            "token": "your-token",
            "pem_file_path": "/path/to/drawio_export_api.pem",
            "verify_tls": True,
            "timeout": 60,
        },
        "top_level_menu": False,
    }
}
```

### Configuration Fields

| Field | Description |
| :--- | :--- |
| `target_models` | Specifies which Netbox class views will have the Ninja tab. This determines where the template output will be displayed in the NetBox interface. |
| `jinja_model_querysets` | Defines which Netbox object types can be used in the Ninja templates. These are the models that can be queried using Jinja2 syntax in your templates. |
| `drawio_export_api.url` | The URL for the [drawio-export-api](https://github.com/rautanen-io/drawio-export-api) service. This is required for SVG image generation. |
| `drawio_export_api.enabled` | Boolean to enable or disable Draw.io Export API integration. |
| `drawio_export_api.token` | Bearer token used to authenticate to the draw.io API. This should be kept secure and not exposed in version control. |
| `drawio_export_api.pem_file_path` | Path to the PEM file used to encrypt data between the plugin and draw.io API. Required when `verify_tls` is enabled. |
| `drawio_export_api.verify_tls` | Whether to use TLS encryption for API communication. If set to `False`, the PEM file is not required. |
| `drawio_export_api.timeout` | Maximum time (in seconds) the plugin will wait for the draw.io export API before closing the connection. |
| `top_level_menu` | If `True`, the plugin is displayed in its own submenu as part of NetBox's navigation menu. If `False`, the plugin is displayed in NetBox's shared "Plugins" menu. |

## Security Considerations

- Keep your API tokens secure and never commit them to version control
- Use TLS encryption (`verify_tls: true`) in production environments
- Regularly rotate your API tokens
- Ensure the PEM file has appropriate permissions and is not accessible to unauthorized users

## Example Configurations

### Development Environment

```python
PLUGINS_CONFIG = {
    "netbox_ninja_plugin": {
        "target_models": {
            "dcim": ["device", "interface", "site", "region"],
        },
        "jinja_model_querysets": {
            "dcim": ["device", "interface", "site", "region"],
        },
        "drawio_export_api": {
            "enabled": True,
            "url": "http://localhost:8080/svg",
            "token": "dev-token",
            "verify_tls": False,
            "timeout": 30,
        },
        "top_level_menu": False,
    }
}
```

### Production Environment

```python
PLUGINS_CONFIG = {
    "netbox_ninja_plugin": {
        "target_models": {
            "dcim": ["device", "interface", "site", "region"],
            "ipam": ["prefix", "vrf", "vlan"],
        },
        "jinja_model_querysets": {
            "dcim": ["device", "interface", "site", "region"],
            "ipam": ["prefix", "vrf", "vlan"],
        },
        "drawio_export_api": {
            "enabled": True,
            "url": "https://drawio-export-api:443/svg",
            "token": "{{ env.DRAWIO_API_TOKEN }}",
            "pem_file_path": "/etc/netbox/drawio_export_api.pem",
            "verify_tls": True,
            "timeout": 60,
        },
        "top_level_menu": False,
    }
}
```
