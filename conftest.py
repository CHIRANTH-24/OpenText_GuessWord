"""Pytest configuration for the project."""
import os
import sys
from pathlib import Path

import django
from django.conf import settings

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Configure Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "guessword.settings")
django.setup()

