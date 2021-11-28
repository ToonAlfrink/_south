from django import template
from random import randint
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag(takes_context=True)
def goat_set_topic_variable(context, title, name):
    context['topic_variable'] = {'title': title, 'name': name}
    return mark_safe(f"<!-- {title}  {name} -->")

_color_names = ['danger', 'dark', 'info', 'success', 'warning']

@register.simple_tag
def goat_random_color():
    return _color_names[randint(0, 100)%len(_color_names)]

@register.simple_tag(takes_context=True)
def goat_step_counter(context):
    context['goat_step_counter'] += 1
    return mark_safe('STEP %02.0f'%context['goat_step_counter'])

