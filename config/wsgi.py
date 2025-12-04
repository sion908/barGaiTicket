"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os
from socket import gethostname

from django.core.wsgi import get_wsgi_application
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
if "fusy-dev" in gethostname():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.setting.develop')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.setting.heroku')
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.setting')
application = get_wsgi_application()

# [Unit]
# Description=gunicorn daemon
# After=network.target

# [Service]
# User=ubuntu
# Group=www-data
# WorkingDirectory=/home/ubuntu/django-aws
# ExecStart=/home/ubuntu/django/bin/gunicorn --access-logfile - --workers 3 --bind unix:/home/ubuntu/django-aws/testapp.sock testapp.wsgi:application

# [Install]
# WantedBy=multi-user.target
