"""
CI / test environment settings.

Uses SQLite in-memory for speed.
"""

from .base import *  # noqa: F401, F403

DEBUG = False
SECRET_KEY = "ci-test-secret-key-not-for-production"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Disable password hashing for speed (passwords stored as plain text anyway)
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
