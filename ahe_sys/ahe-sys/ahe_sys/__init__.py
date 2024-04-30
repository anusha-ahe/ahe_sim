import os
from django.conf import settings
import django
import importlib

if not settings.configured:
    settings_file = os.environ.get("DJANGO_SETTINGS_MODULE")
    settings_module = importlib.import_module(settings_file)
    django.setup()
