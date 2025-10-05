"""WSGI config for guessword project."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "guessword.settings")

application = get_wsgi_application()

