"""
Production settings for Render deployment.

All sensitive values MUST come from environment variables.
"""

from .base import *  # noqa: F401, F403

DEBUG = False

# In production, these MUST be set via env vars
SECRET_KEY = env("SECRET_KEY")  # noqa: F405
ALLOWED_HOSTS = env("ALLOWED_HOSTS")  # noqa: F405

# PostgreSQL on Render (DATABASE_URL is auto-provided by Render)
DATABASES = {
    "default": env.db("DATABASE_URL"),  # noqa: F405
}

# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
