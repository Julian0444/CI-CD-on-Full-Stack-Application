"""
Base settings — shared across all environments.

Environment variables are read via django-environ. Each deployment
environment (local / ci / prod) extends this file.
"""

import os
from pathlib import Path

import environ

# ──────────────────────────── paths ────────────────────────────
# BASE_DIR = /backend
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, "change-me-in-production"),
    ALLOWED_HOSTS=(list, ["*"]),
    FRONT_ORIGINS=(str, ""),
    DATABASE_URL=(str, "sqlite:///db.sqlite3"),
)

# Read .env file if it exists (local / CI)
env_file = BASE_DIR / ".env"
if env_file.is_file():
    env.read_env(str(env_file))

# ──────────────────────────── core ─────────────────────────────
SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

# ──────────────────────────── apps ─────────────────────────────
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
    # Project apps
    "apps.health",
    "apps.users",
    "apps.todos",
]

# ──────────────────────────── middleware ────────────────────────
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    # CSRF disabled for API-only backend (matches Go behaviour)
    # "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ──────────────────────────── database ─────────────────────────
DATABASES = {
    "default": env.db("DATABASE_URL", default="sqlite:///db.sqlite3"),
}

# ──────────────────────────── auth ─────────────────────────────
AUTH_PASSWORD_VALIDATORS = []  # This app stores plain-text passwords (matches Go)

# ──────────────────────────── i18n ─────────────────────────────
LANGUAGE_CODE = "es"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ──────────────────────────── static ───────────────────────────
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ──────────────────────────── DRF ──────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    # No authentication — matches Go backend
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "UNAUTHENTICATED_USER": None,
}

# ──────────────────────────── drf-spectacular ──────────────────
SPECTACULAR_SETTINGS = {
    "TITLE": "Todo App API",
    "DESCRIPTION": "API para gestión de tareas y usuarios.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# ──────────────────────────── CORS ─────────────────────────────
_default_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

_extra = env("FRONT_ORIGINS")
_extra_origins = [o.strip() for o in _extra.split(",") if o.strip()] if _extra else []

CORS_ALLOWED_ORIGINS = list(dict.fromkeys(_default_origins + _extra_origins))
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    "origin",
    "content-type",
    "authorization",
]
CORS_EXPOSE_HEADERS = [
    "content-length",
]
CORS_PREFLIGHT_MAX_AGE = 12 * 60 * 60  # 12 hours

# ──────────────────────────── logging ──────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": os.getenv("LOG_LEVEL", "INFO"),
    },
}
