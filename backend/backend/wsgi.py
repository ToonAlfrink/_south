"""
WSGI config for backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os
import dotenv
import sys

from django.core.wsgi import get_wsgi_application

_ROOT_DIR = os.path.normpath(os.path.join(__file__, '../../..'))
for filename in ['.env.prod' if os.name.lower() != 'nt' else None, '.env']:
    if filename: 
        print('load_w: ' + filename)
        dotenv.read_dotenv(os.path.join(_ROOT_DIR, filename))

sys.path.append(os.path.join(_ROOT_DIR, 'goat_shared'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

application = get_wsgi_application()
