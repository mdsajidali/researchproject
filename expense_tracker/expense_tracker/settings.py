"""
Django settings for expense_tracker project.

Revised for MSc Thesis Deployment (Docker, Kubernetes, Swarm, Nomad, Mesos, OpenShift)
"""

from pathlib import Path
import os
import environ
import socket

# ----------------------------------------------------------------------
# Base directories and environment
# ----------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, "changeme-in-dev"),
    ALLOWED_HOSTS=(list, ["*"]),
    DB_NAME=(str, "expensedb"),
    DB_USER=(str, "expense"),
    DB_PASSWORD=(str, "expensepass"),
    DB_HOST=(str, "db"),
    DB_PORT=(int, 5432),
)
# Load .env file locally; in containers, environment variables are injected
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# ----------------------------------------------------------------------
# Core Django settings
# ----------------------------------------------------------------------
DEBUG = env("DEBUG")
SECRET_KEY = env("SECRET_KEY")
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# Allowed hosts (stable version for all orchestrators)
# ----------------------------------------------------------------------

# Always accept these baseline hosts
default_hosts = ["localhost", "127.0.0.1", "0.0.0.0", "app"]

# Add any IPs discovered at runtime (so container internal IP works)
try:
    default_hosts.append(socket.gethostbyname(socket.gethostname()))
except Exception:
    pass

# Merge with environment variable, if provided
raw_hosts = os.getenv("DJANGO_ALLOWED_HOSTS", "")
if raw_hosts:
    extra_hosts = [h.strip() for h in raw_hosts.replace(" ", "").split(",") if h]
    default_hosts.extend(extra_hosts)

# Final unique list
ALLOWED_HOSTS = list(set(default_hosts))

# ----------------------------------------------------------------------
# Application definition
# ----------------------------------------------------------------------
INSTALLED_APPS = [
    "expenses",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Serve static files efficiently
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "expense_tracker.urls"

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

WSGI_APPLICATION = "expense_tracker.wsgi.application"

# ----------------------------------------------------------------------
# Database Configuration (PostgreSQL for all orchestrators)
# ----------------------------------------------------------------------
# Allow reading DB password from Docker secret file if present
db_pw_file = os.getenv("DB_PASSWORD_FILE")
if db_pw_file and os.path.exists(db_pw_file):
    with open(db_pw_file) as f:
        os.environ["DB_PASSWORD"] = f.read().strip()

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),
    }
}

# ----------------------------------------------------------------------
# Password validation
# ----------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ----------------------------------------------------------------------
# Internationalization
# ----------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ----------------------------------------------------------------------
# Static files (CSS, JavaScript, Images)
# ----------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Enable WhiteNoise compressed caching for production
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ----------------------------------------------------------------------
# Miscellaneous Settings
# ----------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "/login/"

# CSRF trusted origins (expand as needed)
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://*.elasticbeanstalk.com",
    "http://*.elasticbeanstalk.com",
    "https://*.cloud9.eu-west-1.amazonaws.com",
]

# ----------------------------------------------------------------------
# Logging (optional for debugging in orchestration environments)
# ----------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
import logging
logging.getLogger("django.security.DisallowedHost").setLevel(logging.ERROR)

