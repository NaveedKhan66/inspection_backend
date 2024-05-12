#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inspection_backend.settings")
    try:
        from django.core.management import execute_from_command_line
        from users import User
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    execute_from_command_line(sys.argv)
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
    if not User.objects.filter(email=ADMIN_EMAIL):
        User.objects.create_superuser("admin", ADMIN_EMAIL, ADMIN_PASSWORD)


if __name__ == "__main__":
    main()
