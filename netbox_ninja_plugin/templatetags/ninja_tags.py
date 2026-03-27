from django import template

register = template.Library()


@register.simple_tag
def render_object(obj, **context):
    filters = context.pop("filters", None) or {}
    render_context = {**context, **filters}
    return obj.render(**render_context)[0]


@register.filter
def app_label(obj):
    return getattr(obj._meta, "app_label", "")


@register.filter
def model_name(obj):
    return getattr(obj._meta, "model_name", "")


@register.filter
def any_drawio(templates):
    return any(t.output_type == "drawio" for t in templates)


@register.filter
def as_list(obj):
    return [obj]
