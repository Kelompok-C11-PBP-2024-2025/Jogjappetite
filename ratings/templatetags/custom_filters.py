from django import template

register = template.Library()

@register.filter(name='add')
def add(value, arg):
    return value + arg
