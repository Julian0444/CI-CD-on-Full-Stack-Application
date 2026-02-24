"""
Local development settings.
"""

from .base import *  # noqa: F401, F403

DEBUG = True

# SQLite for quick local development
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}
