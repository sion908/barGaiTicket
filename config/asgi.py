"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
from socket import gethostname

from django.core.asgi import get_asgi_application


# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

if "fusy-dev" in gethostname():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.setting.develop')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.setting.heroku')

application = get_asgi_application()
