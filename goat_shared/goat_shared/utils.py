import threading
import traceback

from django.http.response import HttpResponse
from string import Template
import re
from progress.bar import Bar
import os
import logging

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(os.environ.get(name+'.LOG_LEVEL', LOG_LEVEL).upper())
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter())
    logger.addHandler(handler)
    return logger


def apply_template(value, variables):
     return value.safe_substitute(variables) if type(value) == Template else value

def run_task_in_new_thread(callback):
    t = threading.Thread(target=callback)
    t.setDaemon(True)
    t.start()

def str_error(error):
    return "".join(traceback.format_exception(None, error, error.__traceback__))

def decode(source, return_encoding = False):
    data = None
    try:
      data = (source.decode(), 'utf-8')
    except UnicodeDecodeError as e:
        try:
          data = (source.decode('ISO-8859-1'), 'ISO-8859-1')
        except UnicodeDecodeError as e2:
            print('decode errors', e, e2)
            data = (source.decode('utf-16'), 'utf-16')
    
    return data if return_encoding else data[0]

class HttpResponseNotAuthenticated(HttpResponse):
    status_code = 401
    content = 'Not Authenticated'

def sanitize_slug(slug):
    if not slug: return slug
    slug = slug.replace('"', '').lower().strip()
    return re.sub(r'\W+', '-', slug) if ' ' in slug else slug

def sanitize_template_name(name):
    name = name if name else 'default'
    name =  re.sub(r'\W+', '-', name.strip()).lower() if name else 'default'
    name = name if name else 'default'
    name =  re.sub(r'^-+', '', name)
    name =  re.sub(r'-+$', '', name)
    return name

class FakeProgressBar:
    def next(self, n = 1): pass
    def finish(self): pass

def create_progress_bar(text, max) -> Bar:
    return  Bar(text, max=max) if os.environ.get('ENABLE_PROGRESS_BAR', 'false').lower() == 'true' else FakeProgressBar()
