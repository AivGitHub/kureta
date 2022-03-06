#!/usr/bin/env python

import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

    try:
        import secure
    except ImportError:
        raise ImportError(f'Project is not initialized. Please run \' {os.path.realpath(__file__)} server --install\'')

    os.environ.setdefault('DEFAULT_DATABASE_PASSWORD', secure.DEFAULT_DATABASE_PASSWORD)
    os.environ.setdefault('SECRET_KEY', secure.SECRET_KEY)

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
