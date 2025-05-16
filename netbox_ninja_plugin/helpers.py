from __future__ import annotations

import logging
import re
from typing import Dict, List, Type, cast

from core.models import ObjectType
from django.db.models import Model
from django.db.utils import ProgrammingError
from netbox.plugins import get_plugin_config

from netbox_ninja_plugin import config

logger = logging.getLogger(__name__)


def _get_target_models() -> Dict[str, List[str]]:
    """Get the target models configuration from plugin settings.

    Returns:
        Dict[str, List[str]]: A dictionary mapping app labels to lists of model names.
    """
    return get_plugin_config(
        "netbox_ninja_plugin",
        "target_models",
        default=config.default_settings["target_models"],
    )


def _get_jinja_model_querysets() -> Dict[str, List[str]]:
    """Get the Jinja model querysets configuration from plugin settings.

    Returns:
        Dict[str, List[str]]: A dictionary mapping app labels to lists of model names.
    """
    return get_plugin_config(
        "netbox_ninja_plugin",
        "jinja_model_querysets",
        default=config.default_settings["jinja_model_querysets"],
    )


def get_target_model_fully_qualified_names() -> List[str]:
    """Get a list of fully qualified model names (app_label.model_name) for target models.

    Returns:
        List[str]: A list of fully qualified model names.
    """
    classes: List[str] = []
    data = _get_target_models()
    for app_label, model_names in data.items():
        for model_name in model_names:
            classes.append(f"{app_label}.{model_name}")
    return classes


def get_target_model_names() -> List[str]:
    """Get a list of model names for target models.

    Returns:
        List[str]: A list of model names.
    """
    data = _get_target_models()
    return [item for sublist in data.values() for item in sublist]


def get_jinja_model_plural_names() -> List[str]:
    """Get a list of plural verbose names for Jinja models.

    Returns:
        List[str]: A list of plural verbose names.
    """
    object_names: List[str] = []
    jinja_models = get_jinja_model_object_types()
    for model in jinja_models:
        # pylint: disable=protected-access
        object_names.append(
            replace_whitespace_with_underscores(str(model._meta.verbose_name_plural))
        )
    return object_names


def _get_object_types(data: Dict[str, List[str]]) -> List[Type[Model]]:
    """Convert model configuration to actual model classes.

    Args:
        data: A dictionary mapping app labels to lists of model names.

    Returns:
        List[Type[Model]]: A list of model classes.
    """
    classes: List[Type[Model]] = []
    for app_label, model_names in data.items():
        for model_name in model_names:
            try:
                ct = ObjectType.objects.get(app_label=app_label, model=model_name)
                model_class = ct.model_class()
                if model_class is not None:
                    classes.append(cast(Type[Model], model_class))
            # This is expected to happen when Netbox starts and tries to load models
            # that are yet not present in the database.
            except ProgrammingError:
                logger.error("ObjectType for %s.%s not found", app_label, model_name)
    return classes


def get_target_model_object_types() -> List[Type[Model]]:
    """Get the model classes for target models.

    Returns:
        List[Type[Model]]: A list of model classes.
    """
    data = _get_target_models()
    return _get_object_types(data)


def get_jinja_model_object_types() -> List[Type[Model]]:
    """Get the model classes for Jinja models.

    Returns:
        List[Type[Model]]: A list of model classes.
    """
    data = _get_jinja_model_querysets()
    return _get_object_types(data)


def replace_whitespace_with_underscores(string: str) -> str:
    """Replace whitespace with underscores in a string.

    Args:
        string: The string to replace whitespace with underscores in.

    Returns:
        str: The string with whitespace replaced with underscores.
    """
    return re.sub(r"\s+", "_", string)
