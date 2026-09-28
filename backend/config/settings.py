import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

from .environment import (
    database_config,
    env_bool,
    env_int,
    env_list,
)


BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent


load_dotenv(
    PROJECT_ROOT / ".env"
)


SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY"
)


if not SECRET_KEY:
    raise RuntimeError(
        "La variable DJANGO_SECRET_KEY "
        "n'est pas définie."
    )


DEBUG = env_bool(
    "DJANGO_DEBUG",
    default=False,
)


ALLOWED_HOSTS = env_list(
    "DJANGO_ALLOWED_HOSTS",
    default="127.0.0.1,localhost",
)


RENDER_EXTERNAL_HOSTNAME = os.getenv(
    "RENDER_EXTERNAL_HOSTNAME",
    "",
).strip()


if (
    RENDER_EXTERNAL_HOSTNAME
    and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS
):
    ALLOWED_HOSTS.append(
        RENDER_EXTERNAL_HOSTNAME
    )


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "corsheaders",
    "rest_framework",
    "drf_spectacular",
    "gestion",
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
        "BACKEND": (
            "django.template.backends.django.DjangoTemplates"
        ),
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                (
                    "django.template.context_processors.request"
                ),
                (
                    "django.contrib.auth.context_processors.auth"
                ),
                (
                    "django.contrib.messages.context_processors.messages"
                ),
            ],
        },
    },
]


WSGI_APPLICATION = "config.wsgi.application"


DATABASES = database_config(BASE_DIR)


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"


DEFAULT_AUTO_FIELD = (
    "django.db.models.BigAutoField"
)


MEDIA_URL = os.getenv(
    "DJANGO_MEDIA_URL",
    "/media/",
)

MEDIA_ROOT = Path(
    os.getenv(
        "DJANGO_MEDIA_ROOT",
        str(BASE_DIR / "media"),
    )
)


CLOUDINARY_URL = os.getenv(
    "CLOUDINARY_URL",
    "",
).strip()

USE_CLOUDINARY_MEDIA = bool(
    CLOUDINARY_URL
)


STORAGES = {
    "default": {
        "BACKEND": (
            "config.media_storage.CloudinaryMediaStorage"
            if USE_CLOUDINARY_MEDIA
            else (
                "django.core.files.storage."
                "FileSystemStorage"
            )
        ),
    },
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage."
            "CompressedManifestStaticFilesStorage"
        ),
    },
}


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        (
            "rest_framework_simplejwt.authentication."
            "JWTAuthentication"
        ),
        (
            "rest_framework.authentication."
            "SessionAuthentication"
        ),
    ],
    "DEFAULT_SCHEMA_CLASS": (
        "drf_spectacular.openapi.AutoSchema"
    ),
}


SPECTACULAR_SETTINGS = {
    "TITLE": "API de gestion de matériel",
    "DESCRIPTION": (
        "API REST permettant de consulter le catalogue, "
        "de créer et suivre des demandes de matériel, et "
        "d'administrer les demandes et les équipements."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayRequestDuration": True,
        "filter": True,
    },
    "TAGS": [
        {
            "name": "Authentification",
            "description": (
                "Connexion JWT et informations sur "
                "l'utilisateur connecté."
            ),
        },
        {
            "name": "Matériels",
            "description": (
                "Consultation du catalogue disponible."
            ),
        },
        {
            "name": "Demandes",
            "description": (
                "Création et suivi des demandes de matériel."
            ),
        },
        {
            "name": "Administration",
            "description": (
                "Gestion des demandes, du catalogue et des stocks."
            ),
        },
    ],
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=30
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=1
    ),
    "AUTH_HEADER_TYPES": (
        "Bearer",
    ),
}


CORS_ALLOWED_ORIGINS = env_list(
    "DJANGO_CORS_ALLOWED_ORIGINS"
)


CSRF_TRUSTED_ORIGINS = env_list(
    "DJANGO_CSRF_TRUSTED_ORIGINS"
)


SECURE_SSL_REDIRECT = env_bool(
    "DJANGO_SECURE_SSL_REDIRECT",
    default=False,
)

SESSION_COOKIE_SECURE = env_bool(
    "DJANGO_SESSION_COOKIE_SECURE",
    default=False,
)

CSRF_COOKIE_SECURE = env_bool(
    "DJANGO_CSRF_COOKIE_SECURE",
    default=False,
)

SECURE_HSTS_SECONDS = env_int(
    "DJANGO_SECURE_HSTS_SECONDS",
    default=0,
    minimum=0,
)

SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS",
    default=False,
)

SECURE_HSTS_PRELOAD = env_bool(
    "DJANGO_SECURE_HSTS_PRELOAD",
    default=False,
)


SECURE_PROXY_SSL_HEADER = (
    (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )
    if env_bool(
        "DJANGO_USE_X_FORWARDED_PROTO",
        default=False,
    )
    else None
)
