from django import template

register = template.Library()

@register.filter(name='additional_filters')
def additional_filters(value):
    return None

