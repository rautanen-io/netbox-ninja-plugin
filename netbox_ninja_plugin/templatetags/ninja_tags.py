from django import template

register = template.Library()


@register.simple_tag
def render_object(obj, **context):
    return obj.render(**context)[0]


@register.filter
def app_label(obj):
    return getattr(obj._meta, "app_label", "")


@register.filter
def model_name(obj):
    return getattr(obj._meta, "model_name", "")
