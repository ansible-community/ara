import logging
import logging.config
import os
import textwrap

import yaml
from django.utils.crypto import get_random_string
from dynaconf import LazySettings

BASE_DIR = os.environ.get("ARA_BASE_DIR", os.path.expanduser("~/.ara/server"))
DEFAULT_CONFIG = os.path.join(BASE_DIR, "default_config.yaml")

settings = LazySettings(
    GLOBAL_ENV_FOR_DYNACONF="ARA", ENVVAR_FOR_DYNACONF="ARA_SETTINGS", SETTINGS_MODULE_FOR_DYNACONF=DEFAULT_CONFIG
)

# reread BASE_DIR since it might have gotten changed in the config file.
BASE_DIR = settings.get("BASE_DIR", BASE_DIR)

# Django doesn't set up logging until it's too late to use it in settings.py.
# Set it up from the configuration so we can use it.
DEBUG = settings.get("DEBUG", False, "@bool")

LOG_LEVEL = settings.get("LOG_LEVEL", "INFO")
# fmt: off
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"normal": {"format": "%(asctime)s %(levelname)s %(name)s: %(message)s"}},
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "normal",
            "level": LOG_LEVEL,
            "stream": "ext://sys.stdout",
        }
    },
    "loggers": {
        "ara": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": 0
        }
    },
    "root": {
        "handlers": ["console"],
        "level": LOG_LEVEL
    },
}
# fmt: on
logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)
logger.debug("Loaded logging configuration")

# Django built-in server and npm development server
ALLOWED_HOSTS = settings.get("ALLOWED_HOSTS", ["::1", "127.0.0.1", "localhost"])
CORS_ORIGIN_WHITELIST = settings.get("CORS_ORIGIN_WHITELIST", ["127.0.0.1:8000", "localhost:3000"])
CORS_ORIGIN_ALLOW_ALL = settings.get("CORS_ORIGIN_ALLOW_ALL", False)

ADMINS = settings.get("ADMINS", ())


def get_secret_key():
    if not settings.get("SECRET_KEY"):
        logger.warn(f"No configuration found for SECRET_KEY. Generating a random key...")
        return get_random_string(length=50)
    return settings.get("SECRET_KEY")


SECRET_KEY = get_secret_key()

# We're not expecting ARA to use multiple concurrent databases.
# Make it easier for users to specify the configuration for a single database.
DATABASE_ENGINE = settings.get("DATABASE_ENGINE", "django.db.backends.sqlite3")
DATABASE_NAME = settings.get("DATABASE_NAME", os.path.join(BASE_DIR, "ansible.sqlite"))
DATABASE_USER = settings.get("DATABASE_USER", None)
DATABASE_PASSWORD = settings.get("DATABASE_PASSWORD", None)
DATABASE_HOST = settings.get("DATABASE_HOST", None)
DATABASE_PORT = settings.get("DATABASE_PORT", None)

DATABASES = {
    "default": {
        "ENGINE": DATABASE_ENGINE,
        "NAME": DATABASE_NAME,
        "USER": DATABASE_USER,
        "PASSWORD": DATABASE_PASSWORD,
        "HOST": DATABASE_HOST,
        "PORT": DATABASE_PORT,
    }
}

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "django_filters",
    "ara.api",
    "ara.server.apps.AraAdminConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

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
            ]
        },
    }
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

USE_TZ = True
TIME_ZONE = "UTC"

USE_I18N = True
USE_L10N = True
LANGUAGE_CODE = "en-us"

STATIC_URL = settings.get("STATIC_URL", "/static/")
STATIC_ROOT = settings.get("STATIC_ROOT", os.path.join(BASE_DIR, "www", "static"))

MEDIA_URL = settings.get("MEDIA_URL", "/media/")
MEDIA_ROOT = settings.get("MEDIA_ROOT", os.path.join(BASE_DIR, "www", "media"))

WSGI_APPLICATION = "ara.server.wsgi.application"
ROOT_URLCONF = "ara.server.urls"
APPEND_SLASH = False
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 100,
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ),
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

ARA_SETTINGS = os.getenv("ARA_SETTINGS", DEFAULT_CONFIG)
logger.info(f"Using configuration file: {ARA_SETTINGS}")

# Ensure default base configuration/data directory exists
if not os.path.isdir(BASE_DIR):
    logger.info(f"Creating data & configuration directory: {BASE_DIR}")
    os.makedirs(BASE_DIR, mode=0o700)

# TODO: Split this out to a CLI command (django-admin command ?)
if not os.path.exists(DEFAULT_CONFIG) and "ARA_SETTINGS" not in os.environ:
    CONFIG = dict(
        BASE_DIR=BASE_DIR,
        ALLOWED_HOSTS=ALLOWED_HOSTS,
        CORS_ORIGIN_WHITELIST=CORS_ORIGIN_WHITELIST,
        CORS_ORIGIN_ALLOW_ALL=CORS_ORIGIN_ALLOW_ALL,
        SECRET_KEY=SECRET_KEY,
        DATABASES=DATABASES,
        STATIC_URL=STATIC_URL,
        STATIC_ROOT=STATIC_ROOT,
        MEDIA_URL=MEDIA_URL,
        MEDIA_ROOT=MEDIA_ROOT,
        DEBUG=DEBUG,
        LOG_LEVEL=LOG_LEVEL,
        LOGGING=LOGGING,
    )
    with open(DEFAULT_CONFIG, "w+") as config_file:
        comment = f"""
        ---
        # This is a default configuration template generated by ARA.
        # To use a configuration file such as this one, you need to export the
        # ARA_SETTINGS configuration variable like so:
        #   $ export ARA_SETTINGS={DEFAULT_CONFIG}

        """
        logger.info(f"Writing default config to {DEFAULT_CONFIG}")
        config_file.write(textwrap.dedent(comment))
        yaml.dump({"default": CONFIG}, config_file, default_flow_style=False)
