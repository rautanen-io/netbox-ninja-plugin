from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Type, cast

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


def get_filter_variable_prefix() -> str:
    """Return the configured Jinja variable prefix for Ninja tab filters."""
    return get_plugin_config(
        "netbox_ninja_plugin",
        "filter_variable_prefix",
        default=config.default_settings["filter_variable_prefix"],
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


def get_model_names() -> List[str]:
    """Get a list of model names for target models.

    Returns:
        List[str]: A list of model names.
    """
    data = _get_target_models()
    return [item for sublist in data.values() for item in sublist]


def get_jinja_model_names() -> List[str]:
    """Get a list of model names for Jinja models.

    The returned list is derived from the plugin setting ``jinja_model_querysets``.

    Returns:
        List[str]: A list of model names.
    """
    data = _get_jinja_model_querysets()
    return [item for sublist in data.values() for item in sublist]


def get_jinja_model_plural_names() -> List[str]:
    """Get a list of plural verbose names for Jinja models.

    Returns:
        List[str]: A list of plural verbose names.
    """
    object_names: List[str] = []
    jinja_models = get_jinja_model_object_types()
    for model in jinja_models:
        object_names.append(_get_plural_var_suffix(model))
    return object_names


def _get_plural_var_suffix(model_class: Type[Model]) -> str:
    """Get snake_case plural suffix for a model's verbose plural name."""
    # pylint: disable=protected-access
    return replace_whitespace_with_underscores(
        str(model_class._meta.verbose_name_plural)
    )


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


def get_filter_variable_name(object_type: ObjectType) -> str:
    """Return the Jinja/context variable name for a selected filter object type.

    The variable name is derived from the model's ``verbose_name_plural`` and
    converted to snake_case.
    Example: "Device type" -> "device_types".
    """
    model_class = object_type.model_class()
    if model_class is None:
        # Fall back to the raw object type model identifier; better than crashing.
        suffix = str(object_type.model).lower()
        # Best-effort pluralization for the removed/invalid-model fallback.
        if not suffix.endswith("s"):
            suffix += "s"
        return f"{get_filter_variable_prefix()}{suffix}"

    return f"{get_filter_variable_prefix()}{_get_plural_var_suffix(model_class)}"


def get_string_filter_variable_name(key: str) -> str:
    """Return the Jinja/context variable name for a string filter key."""
    prefix = get_filter_variable_prefix()
    if key.startswith(prefix):
        return key
    return f"{prefix}{key}"


def get_viewable_queryset_for_user(model_class: Type[Model], user: Any):
    """Return a queryset of instances the user may view (NetBox object-level permissions).

    Uses ``RestrictedQuerySet.restrict()`` when available so Ninja tab object filters
    match list/detail access. Falls back to an unrestricted queryset only if the model
    does not use NetBox's restricted manager (e.g. some third-party types).
    """
    qs = model_class.objects.all()
    restrict = getattr(qs, "restrict", None)
    if callable(restrict):
        return restrict(user, "view")
    logger.warning(
        "Model %s has no restrict(); Ninja tab object filter queryset is unrestricted.",
        model_class._meta.label_lower,
    )
    return qs
