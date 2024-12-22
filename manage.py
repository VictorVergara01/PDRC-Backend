#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from decouple import config


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestor_revistas.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

print("DATABASE CONFIG:")
print("NAME:", config('MYSQLDATABASE'))
print("USER:", config('MYSQLUSER'))
print("PASSWORD:", config('MYSQLPASSWORD'))
print("HOST:", config('MYSQLHOST'))
print("PORT:", config('DEBUG'))
print("PORT:", config('ALLOWED_HOSTS'))

if __name__ == '__main__':
    main()