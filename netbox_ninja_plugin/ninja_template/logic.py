from __future__ import annotations

import io
import xml.etree.ElementTree as ET
from typing import Any, Dict, List

import requests
from django.db.models import Model
from netbox.plugins import get_plugin_config

from netbox_ninja_plugin import config
from netbox_ninja_plugin.helpers import (
    get_jinja_model_object_types,
    replace_whitespace_with_underscores,
)


class NinjaTemplateMixin:
    """A mixin class that provides template rendering functionality.

    This mixin provides methods for getting context data for template rendering
    and handling draw.io diagram exports.
    """

    def get_context(self, **context: Any) -> Dict[str, List[Model]]:
        """Get a context dictionary containing querysets for all Jinja models.

        Args:
            **context: Additional context variables to include in the returned dictionary.

        Returns:
            Dict[str, List[Model]]: A dictionary containing querysets for all configured
                                   Jinja models, keyed by their verbose plural names.
        """
        jinja_models = get_jinja_model_object_types()

        for model in jinja_models:
            data = model.objects.all()
            # pylint: disable=protected-access
            key = replace_whitespace_with_underscores(
                str(model._meta.verbose_name_plural)
            )
            context[key] = data

        return context

    def _add_svgdata_ids(self, svg_string):
        namespaces = {
            "svg": "http://www.w3.org/2000/svg",
            "xlink": "http://www.w3.org/1999/xlink",
        }
        ET.register_namespace("", namespaces["svg"])
        ET.register_namespace("xlink", namespaces["xlink"])

        try:
            root = ET.fromstring(svg_string)
        except ET.ParseError as e:
            return svg_string

        for g_element in root.findall(
            ".//svg:g[@data-cell-id]", namespaces={"svg": namespaces["svg"]}
        ):
            data_cell_id = g_element.get("data-cell-id")

            if data_cell_id:
                inner_g = ET.Element(f"{{{namespaces['svg']}}}g")
                inner_g.set("id", f"cell-{data_cell_id}")

                children_to_move = list(g_element)
                for child in children_to_move:
                    g_element.remove(child)
                    inner_g.append(child)

                g_element.append(inner_g)

        svg_element_and_content_str = ET.tostring(
            root, encoding="unicode", method="xml"
        )

        xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
        doctype_str = '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n'

        final_transformed_svg_string = (
            xml_declaration + doctype_str + svg_element_and_content_str
        )

        return final_transformed_svg_string

    def drawio_export_api_client(self, drawio_xml: str) -> str:
        """Convert a draw.io XML diagram to SVG using an external API.

        Args:
            drawio_xml (str): The draw.io XML diagram to convert.

        Returns:
            str: The SVG representation of the diagram.

        Note:
            This method uses the draw.io export API configured in the plugin settings.
            The API endpoint, authentication token, and TLS settings are configurable.
        """
        api_params = get_plugin_config(
            "netbox_ninja_plugin",
            "drawio_export_api",
            default=config.default_settings["drawio_export_api"],
        )

        file_obj = io.StringIO(drawio_xml)
        files = {"file": ("image.drawio", file_obj, "application/xml")}

        response = requests.post(
            api_params["url"],
            files=files,
            headers={"Authorization": f"""Bearer {api_params["token"]}"""},
            verify=api_params["pem_file_path"] if api_params["verify_tls"] else False,
            timeout=api_params["timeout"],
        )

        xml_string_with_svg_data = self._add_svgdata_ids(
            response.content.decode("utf-8")
        )

        return xml_string_with_svg_data
