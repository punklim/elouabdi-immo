"""Réglages du site. En local, tout fonctionne sans configuration.
En production, les valeurs sensibles viennent de variables d'environnement
(voir .env.example et DEPLOIEMENT.md)."""
import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

from .agence import AGENCE  # noqa: F401  (utilisé par biens/context_processors.py)

BASE_DIR = Path(__file__).resolve().parent.parent


def env(name, default=""):
    return os.environ.get(name, default)


def env_list(name, default=""):
    return [v.strip() for v in env(name, default).split(",") if v.strip()]


DEBUG = env("DJANGO_DEBUG", "1") == "1"

SECRET_KEY = env("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "cle-de-developpement-non-securisee"
    else:
        raise ImproperlyConfigured("DJANGO_SECRET_KEY est obligatoire en production.")

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost")
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS")
SITE_URL = env("SITE_URL", "http://127.0.0.1:8000").rstrip("/")

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "cloudinary_storage",
    "cloudinary",
    "django.contrib.humanize",
    "django.contrib.sitemaps",
    "biens",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
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
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "biens.context_processors.agence",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / env('DB_NAME', 'db.sqlite3')}",
        conn_max_age=600,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Langues : français par défaut, arabe sous /ar/
LANGUAGE_CODE = "fr"
LANGUAGES = [
    ("fr", "Français"),
    ("en", "English"),
    ("ar", "العربية"),
]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "Africa/Casablanca"
USE_I18N = True
USE_TZ = True

# Fichiers statiques et photos des biens
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {"BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# E-mails : affichés dans le terminal tant qu'aucun serveur SMTP n'est configuré
if env("EMAIL_HOST"):
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = env("EMAIL_HOST")
    EMAIL_PORT = int(env("EMAIL_PORT", "587"))
    EMAIL_HOST_USER = env("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
    EMAIL_USE_TLS = env("EMAIL_USE_TLS", "1") == "1"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", AGENCE["email"])

# Sécurité (activée automatiquement hors mode développement)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_CONTENT_TYPE_NOSNIFF = True

# --- Configuration Jazzmin pour l'Admin ---
JAZZMIN_SETTINGS = {
    "show_ui_builder": False,
    "use_bootswatch": False,
    "site_title": "El Ouabdi Admin",
    "site_header": "El Ouabdi Immobilier",
    "site_brand": "El Ouabdi",
    "welcome_sign": "Bienvenue sur l'administration",
    "copyright": "El Ouabdi Immobilier",
    "search_model": ["biens.Bien"],

    # Feuille de style personnalisée (doit être ici, pas dans JAZZMIN_UI_TWEAKS)
    "custom_css": "css/admin-custom.css",
       "custom_js": "js/admin-custom.js",

    # Menu de gauche
    "show_sidebar": True,
    "navigation_expanded": False,

    # Icônes
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "biens.Bien": "fas fa-building",
        "biens.Ville": "fas fa-city",
        "biens.Agent": "fas fa-user-tie",
        "biens.Demande": "fas fa-envelope",
        "biens.Avis": "fas fa-star",
        "biens.Article": "fas fa-newspaper",
    },

    "order_with_respect_to": ["biens", "auth"],

    # Lien personnalisé vers la page Statistiques
    "custom_links": {
        "biens": [{
            "name": "Statistiques",
            "url": "admin:statistiques",
            "icon": "fas fa-chart-line",
            "permissions": ["biens.view_bien"],
        }]
    },
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-warning",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": True,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": "default",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}

# Logging pour voir les erreurs en production
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
        "level": "ERROR",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
WHITENOISE_MANIFEST_STRICT = False

# Configuration Cloudinary pour le stockage des médias.
# ATTENTION : à remplacer par env("CLOUDINARY_...") dès que les nouvelles
# clés sont enregistrées sur Render (voir les explications).
if env("CLOUDINARY_API_SECRET"):
    CLOUDINARY_STORAGE = {
        "CLOUD_NAME": env("deqjnutse"),
        "API_KEY": env("836895945435488"),
        "API_SECRET": env("O5WTZQSH6ZiyWqfUpDJO3ZYya6E"),
    }
elif DEBUG:
    STORAGES["default"] = {"BACKEND": "django.core.files.storage.FileSystemStorage"}
else:
    raise ImproperlyConfigured("Les variables CLOUDINARY_* sont obligatoires en production.")