
from frontend.img_manager import img_data_manager
from django import template

import re
import random
import os

register = template.Library()

BUCKET_MEDIA_PREFIX = os.environ['BUCKET_MEDIA_PREFIX']
SPACES_URL = os.environ['SPACES_URL']

@register.filter
def goat_range(start, end): return range(start, end)

@register.filter
def goat_img_url(name):
    return f'{SPACES_URL}{BUCKET_MEDIA_PREFIX}{name}/{img_data_manager.next_file(name)}'

@register.filter
def interlinks_chunk(array):
    if len(array) == 0: return []
    links = []
    for _ in range(0, 10):
        links.append(array.pop(0))
        if len(array) == 0: return links
    return links

@register.filter
def goat_shuffled_range(start, end): 
    t = list(range(start, end))
    random.shuffle(t)
    return t

@register.filter
def goat_lang_part(lang_iso_code):
    if not lang_iso_code or not re.match(r'\w+-\w+', lang_iso_code): return 'en'
    return lang_iso_code[0:lang_iso_code.index('-')]
