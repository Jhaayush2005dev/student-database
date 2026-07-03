"""
WSGI config for student_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.management import call_command
from django.core.wsgi import get_wsgi_application
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_project.settings')

application = get_wsgi_application()

try:
    import django

    django.setup()
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auth_user'")
        if not cursor.fetchone():
            call_command('migrate', interactive=False, verbosity=0)
except Exception:
    pass
