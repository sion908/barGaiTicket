#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from socket import gethostname


def main():
    """Run administrative tasks."""
    if "fusy-dev" in gethostname():
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.setting.develop')
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.setting.heroku')
    # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.setting.')
    # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.setting')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
