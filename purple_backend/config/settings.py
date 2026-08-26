"""
Django settings for purple_backend project.
"""
import os
from datetime import timedelta
from decouple import config
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-change-me-in-production-n^q=98d^ke0m3nu80!2gs",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if origin.strip()
]
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")


INSTALLED_APPS = [
     # dashboard must precede unfold/admin so our admin/index.html override is
        # discovered first; it then {% extends "admin/index.html" %} to chain
        # into unfold's own (which itself extends Django's), rather than
        # duplicating unfold's markup.
    "dashboard",
    
    "unfold",  # must precede django.contrib.admin
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "colorfield",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "cloudinary",

    # third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_filters",

    # purple apps
    "accounts",
    "salons",
    "services",
    "stylists",
    "bookings",
    "notifications",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
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
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"




import dj_database_url

DATABASES = {
    "default": dj_database_url.config(
        default=config("DATABASE_URL")
    )
}

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Accra"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"



MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Media storage: use Cloudinary whenever CLOUDINARY_URL is configured (production).
# Falls back to local disk for local dev — NOT durable on Render, whose filesystem
# is wiped on every redeploy/restart, which is why uploaded avatars/portfolio
# images disappear (404) after a deploy unless Cloudinary is configured.
if os.environ.get("CLOUDINARY_URL"):
    CLOUDINARY_STORAGE = {"MEDIA_TAG": "purple"}


STORAGES = {
    "default": {
        "BACKEND": (
            "cloudinary_storage.storage.MediaCloudinaryStorage"
            if os.environ.get("CLOUDINARY_URL")
            else "django.core.files.storage.FileSystemStorage"
        ),
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- DRF ---
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=6),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=14),
    "ROTATE_REFRESH_TOKENS": True,
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# --- CORS (React dev server) ---
CORS_ALLOWED_ORIGINS = os.environ.get(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000",
).split(",")
CORS_ALLOW_CREDENTIALS = True

# --- Admin branding ---
ADMIN_SITE_HEADER = "Purple Admin"
ADMIN_SITE_TITLE = "Purple Admin Portal"
ADMIN_INDEX_TITLE = "Manage your salon platform"

X_FRAME_OPTIONS = "SAMEORIGIN"  

# --- SMS (Arkesel — Ghana SMS gateway) ---
SMS_PROVIDER = os.environ.get("SMS_PROVIDER", "arkesel")
ARKESEL_API_KEY = os.environ.get("ARKESEL_API_KEY", "")
ARKESEL_SENDER_ID = os.environ.get("ARKESEL_SENDER_ID", "Purple")
SMS_ENABLED = os.environ.get("SMS_ENABLED", "True") == "True"

# --- Django Unfold (admin theme) ---
# COLORS uses a violet OKLCH scale matching Purple's brand accent; gold is
# introduced separately, inside our own dashboard template content, as the
# secondary restrained accent — not as a global admin color, to keep this a
# single deliberate accent rather than two competing brand colors everywhere.
UNFOLD = {
    "SITE_TITLE": "Purple Admin",
    "SITE_HEADER": "Purple Admin",
    "SITE_SYMBOL": "storefront",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "ENVIRONMENT": "dashboard.utils.environment_callback",
    "DASHBOARD_CALLBACK": "dashboard.utils.dashboard_callback",
    "COLORS": {
        "primary": {
            "50": "oklch(97.7% 0.014 308.299)",
            "100": "oklch(94.6% 0.033 307.174)",
            "200": "oklch(90.2% 0.060 306.703)",
            "300": "oklch(82.7% 0.108 306.383)",
            "400": "oklch(72.2% 0.177 305.504)",
            "500": "oklch(62.7% 0.233 303.900)",
            "600": "oklch(55.8% 0.252 302.321)",
            "700": "oklch(49.6% 0.237 301.924)",
            "800": "oklch(43.8% 0.198 303.724)",
            "900": "oklch(38.1% 0.166 304.987)",
            "950": "oklch(29.1% 0.143 302.717)",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
    },
}
