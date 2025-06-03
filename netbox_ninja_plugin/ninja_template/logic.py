from __future__ import annotations

import io
from typing import Any, Dict, List

import requests
from django.db.models import Model
from lxml import etree
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

    def imitate_drawio_svgdata_plugin(self, svg_input: str) -> str:
        """
        This svg manipulation is needed by Grafana's Flow plugin.

        Ideally it should be part of draw.io export API but currently
        it's not supported:

        More context:
        https://grafana.com/grafana/plugins/andrewbmchugh-flow-panel/
        https://github.com/rlespinasse/drawio-export/issues/139
        https://github.com/jgraph/drawio/blob/dev/src/main/webapp/plugins/svgdata.js
        https://github.com/jgraph/drawio/issues/3225#issuecomment-1336910173
        """

        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.fromstring(svg_input.encode("utf-8"), parser)

        for g_elem in tree.xpath(
            ".//svg:g[@data-cell-id]", namespaces={"svg": "http://www.w3.org/2000/svg"}
        ):
            data_cell_id = g_elem.get("data-cell-id")
            new_g = etree.Element(
                "{http://www.w3.org/2000/svg}g", id=f"cell-{data_cell_id}"
            )

            for child in list(g_elem):
                g_elem.remove(child)
                new_g.append(child)

            g_elem.append(new_g)

        return etree.tostring(tree, pretty_print=True, encoding="unicode")

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

        svg = response.content.decode("utf-8")
        svg_with_svgdata = self.imitate_drawio_svgdata_plugin(svg)

        return svg_with_svgdata
