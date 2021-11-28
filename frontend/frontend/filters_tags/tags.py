from django import template
from random import randint
from django.utils.safestring import mark_safe
import re
from goat_shared.utils import sanitize_slug

register = template.Library()

@register.simple_tag(takes_context=True)
def goat_value_title(context, index):
    return context.get(f'value0{index}Title' if index < 10 else f'value{index}Title')


_color_names = ['danger', 'dark', 'info', 'success', 'warning']

@register.simple_tag(takes_context=True)
def chip_text(context, field = None):
    if not field: return context['chip_data'].pop()['__row'][0]
    return context['chip_data'].pop().get(field + 'Chip')

@register.simple_tag
def goat_random_color():
    return _color_names[randint(0, 100)%len(_color_names)]

@register.simple_tag(takes_context=True)
def nth_interlink_title(context, n):
    return context.get(f'interlink0{n}Title')


@register.simple_tag
def goat_random_pop(array):
    if len(array) != 0:
        return array.pop(randint(0, len(array) - 1))
    else:
        return '|--N/A--|'

@register.simple_tag(takes_context=True)
def goat_values_title(context):
    return goat_random_pop(context['values_titles'])

@register.simple_tag()
def goat_href(slug):
    if not slug or slug.startswith('http://') or slug.startswith('https://'):
        return mark_safe(f'href="{slug}" target="_blank"')
    
    return mark_safe(f'href="{sanitize_slug(slug)}"')

