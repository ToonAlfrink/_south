from django import template
from goat_shared.utils import str_error
from datetime import datetime

register = template.Library()

@register.filter

@register.filter
def serialize_error(err):
    return str_error(err) if err else ''

@register.filter
def goat_range(start, end): return range(start, end)

@register.filter
def goat_count_str(n): return f'0{n}' if n < 10 else str(n)

@register.filter
def goat_format_date_from_seconds(time):
    if not type(time) == int and not type(time) == float: return time
    return datetime.fromtimestamp(time).strftime('%a, %d %b %Y %H:%M:%S -0500')

@register.filter
def goat_ram_readable(value):
    if not type(value) == int:
        return value
    return f'{value >> 20}Mb'
