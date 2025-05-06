from django import template

register = template.Library()


@register.simple_tag
def render_object(obj, **context):
    return obj.render(**context)
