#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
# oauth2는 ssl 레이어를 이용함. 이것을 허용하도록 환경변수를 설정하는 것

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RelolerApi.settings')
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
