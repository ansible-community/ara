# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import textwrap
import warnings

import tzlocal
from django.utils.crypto import get_random_string
from dynaconf import LazySettings

# dynaconf prefers ruamel.yaml but historically we also used pyyaml
# https://github.com/rochacbruno/dynaconf/commit/d5cf87cbbdf54625ccf1138a4e4c210956791e61
# ruamel.yaml >= 0.18 deprecated raw use of .dump
# https://github.com/ansible-community/ara/issues/524
from ruamel.yaml import YAML

yaml = YAML(typ="unsafe", pure=True)
yaml.default_flow_style = False

BASE_DIR = os.environ.get("ARA_BASE_DIR", os.path.expanduser("~/.ara/server"))
DEFAULT_SETTINGS = os.path.join(BASE_DIR, "settings.yaml")

settings = LazySettings(
    environments=True,
    ENVVAR_PREFIX_FOR_DYNACONF="ARA",
    ENVVAR_FOR_DYNACONF="ARA_SETTINGS",
    SETTINGS_FILE_FOR_DYNACONF=DEFAULT_SETTINGS,
)

# reread BASE_DIR since it might have gotten changed in the config file.
BASE_DIR = settings.get("BASE_DIR", BASE_DIR)

# Deploy ARA on a subpath, useful when behind a reverse proxy
# NOTE: This also modifies stuff like STATIC_URL
BASE_PATH = settings.get("BASE_PATH", "/")

# Django doesn't set up logging until it's too late to use it in settings.py.
# Set it up from the configuration so we can use it.
DEBUG = settings.get("DEBUG", False, "@bool")

LOG_LEVEL = settings.get("LOG_LEVEL", "INFO")
# default logger updated cf issue https://github.com/ansible-community/ara/issues/228
# and PR https://github.com/ansible-community/ara/pull/367
LOGGING = settings.get(
    "LOGGING",
    {
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
        "loggers": {"ara": {"handlers": ["console"], "level": LOG_LEVEL, "propagate": 0}},
    },
).to_dict()

if "root" in LOGGING:
    print(
        "[ara] Server's LOGGING configuration has a 'root' logger which is deprecated after version 1.5.8 "
        "due to conflicts. Please update your settings.yaml or generate a new one by "
        "removing it from ara's configuration folder"
    )
    del LOGGING["root"]

# Django built-in server and npm development server
ALLOWED_HOSTS = settings.get("ALLOWED_HOSTS", ["::1", "127.0.0.1", "localhost"])
CORS_ORIGIN_WHITELIST = settings.get("CORS_ORIGIN_WHITELIST", ["http://127.0.0.1:8000", "http://localhost:3000"])
CORS_ORIGIN_REGEX_WHITELIST = settings.get("CORS_ORIGIN_REGEX_WHITELIST", [])
CORS_ORIGIN_ALLOW_ALL = settings.get("CORS_ORIGIN_ALLOW_ALL", False)
CSRF_TRUSTED_ORIGINS = settings.get("CSRF_TRUSTED_ORIGINS", [])

ADMINS = settings.get("ADMINS", ())

READ_LOGIN_REQUIRED = settings.get("READ_LOGIN_REQUIRED", False, "@bool")
WRITE_LOGIN_REQUIRED = settings.get("WRITE_LOGIN_REQUIRED", False, "@bool")
EXTERNAL_AUTH = settings.get("EXTERNAL_AUTH", False, "@bool")


def get_secret_key():
    if not settings.get("SECRET_KEY"):
        print("[ara] No setting found for SECRET_KEY. Generating a random key...")
        return get_random_string(length=50)
    return settings.get("SECRET_KEY")


SECRET_KEY = get_secret_key()

# Whether or not to enable the distributed sqlite database backend and WSGI application.
DISTRIBUTED_SQLITE = settings.get("DISTRIBUTED_SQLITE", False)

# Under which URL should requests be delegated to the distributed sqlite wsgi application
DISTRIBUTED_SQLITE_PREFIX = settings.get("DISTRIBUTED_SQLITE_PREFIX", "ara-report")

# Root directory under which databases will be found relative to the requested URLs.
# This will restrict where the WSGI application will go to seek out databases.
# For example, the URL "example.org/some/path/ara-report" would translate to
# "/var/www/logs/some/path/ara-report" instead of "/some/path/ara-report".
DISTRIBUTED_SQLITE_ROOT = settings.get("DISTRIBUTED_SQLITE_ROOT", "/var/www/logs")

WSGI_APPLICATION = "ara.server.wsgi.application"

# We're not expecting ARA to use multiple concurrent databases.
# Make it easier for users to specify the configuration for a single database.
DATABASE_ENGINE = settings.get("DATABASE_ENGINE", "django.db.backends.sqlite3")
DATABASE_NAME = settings.get("DATABASE_NAME", os.path.join(BASE_DIR, "ansible.sqlite"))
DATABASE_USER = settings.get("DATABASE_USER", None)
DATABASE_PASSWORD = settings.get("DATABASE_PASSWORD", None)
DATABASE_HOST = settings.get("DATABASE_HOST", None)
DATABASE_PORT = settings.get("DATABASE_PORT", None)
DATABASE_CONN_MAX_AGE = settings.get("DATABASE_CONN_MAX_AGE", 0)
DATABASE_OPTIONS = settings.get("DATABASE_OPTIONS", {})

DATABASES = {
    "default": {
        "ENGINE": "ara.server.db.backends.distributed_sqlite" if DISTRIBUTED_SQLITE else DATABASE_ENGINE,
        "NAME": DATABASE_NAME,
        "USER": DATABASE_USER,
        "PASSWORD": DATABASE_PASSWORD,
        "HOST": DATABASE_HOST,
        "PORT": DATABASE_PORT,
        "CONN_MAX_AGE": DATABASE_CONN_MAX_AGE,
        "OPTIONS": DATABASE_OPTIONS,
    }
}

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "health_check",
    "health_check.db",
    "corsheaders",
    "rest_framework",
    "django_filters",
    "ara.api",
    "ara.ui",
    "ara.server.apps.AraAdminConfig",
    # NOTE: django_extensions is not currently meant to be enabled except for the single purpose of generating
    #       a database graph for the documentation.
    # See:
    # - doc/source/_graphs/database_graph_model.sh
    # - https://django-extensions.readthedocs.io/en/latest/installation_instructions.html
    # - https://django-extensions.readthedocs.io/en/latest/graph_models.html
    # "django_extensions",
]

EXTERNAL_AUTH_MIDDLEWARE = []
if EXTERNAL_AUTH:
    EXTERNAL_AUTH_MIDDLEWARE = ["django.contrib.auth.middleware.RemoteUserMiddleware"]
    AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.RemoteUserBackend"]
    REST_FRAMEWORK_AUTH = ("rest_framework.authentication.RemoteUserAuthentication",)
else:
    REST_FRAMEWORK_AUTH = ("rest_framework.authentication.BasicAuthentication",)

# fmt: off
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
] + EXTERNAL_AUTH_MIDDLEWARE + [
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware"
]
# fmt: on

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
                "ara.server.context_processors.about",
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
# Under some circumstances tzlocal can't find the local timezone, it will return local or None
# Default to UTC if this happens.
# https://github.com/ansible-community/ara/issues/401
LOCAL_TIME_ZONE = tzlocal.get_localzone_name()
if LOCAL_TIME_ZONE is None or LOCAL_TIME_ZONE == "local":
    LOCAL_TIME_ZONE = "UTC"
TIME_ZONE = settings.get("TIME_ZONE", LOCAL_TIME_ZONE)

# We do not currently support internationalization and localization, turn these
# off.
USE_I18N = False
USE_L10N = False

# whitenoise serves static files without needing to use "collectstatic"
WHITENOISE_USE_FINDERS = True
# https://github.com/evansd/whitenoise/issues/215
# Whitenoise raises a warning if STATIC_ROOT doesn't exist
warnings.filterwarnings("ignore", message="No directory at", module="whitenoise.base")
# https://github.com/ansible-community/ara/issues/492
# Django expects a ~/.ara/www/static directory but there is no such thing
warnings.filterwarnings("ignore", message="No directory at", module="django.core.handlers.base")

STATIC_URL = settings.get("STATIC_URL", "/static/")
STATIC_ROOT = settings.get("STATIC_ROOT", os.path.join(BASE_DIR, "www", "static"))
MEDIA_URL = settings.get("MEDIA_URL", "/media/")
MEDIA_ROOT = settings.get("MEDIA_ROOT", os.path.join(BASE_DIR, "www", "media"))

ROOT_URLCONF = "ara.server.urls"
APPEND_SLASH = False

PAGE_SIZE = settings.get("PAGE_SIZE", 100)

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": PAGE_SIZE,
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "ara.api.renderers.BrowsableAPIRendererWithoutForms",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": REST_FRAMEWORK_AUTH,
    "DEFAULT_PERMISSION_CLASSES": ("ara.api.auth.APIAccessPermission",),
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "UNICODE_JSON": False,
}

ARA_SETTINGS = os.getenv("ARA_SETTINGS", DEFAULT_SETTINGS)

# TODO: Split this out to a CLI command (django-admin command ?)

# Ensure default base configuration/data directory exists
if not os.path.isdir(BASE_DIR):
    print("[ara] Creating data & configuration directory: %s" % BASE_DIR)
    os.makedirs(BASE_DIR, mode=0o700)

if not os.path.exists(DEFAULT_SETTINGS) and "ARA_SETTINGS" not in os.environ:
    SETTINGS = dict(
        BASE_DIR=BASE_DIR,
        BASE_PATH=BASE_PATH,
        ALLOWED_HOSTS=ALLOWED_HOSTS.to_list(),
        CORS_ORIGIN_WHITELIST=CORS_ORIGIN_WHITELIST.to_list(),
        CORS_ORIGIN_REGEX_WHITELIST=CORS_ORIGIN_REGEX_WHITELIST.to_list(),
        CORS_ORIGIN_ALLOW_ALL=CORS_ORIGIN_ALLOW_ALL,
        CSRF_TRUSTED_ORIGINS=CSRF_TRUSTED_ORIGINS.to_list(),
        EXTERNAL_AUTH=EXTERNAL_AUTH,
        SECRET_KEY=SECRET_KEY,
        DATABASE_ENGINE=DATABASE_ENGINE,
        DATABASE_NAME=DATABASE_NAME,
        DATABASE_USER=DATABASE_USER,
        DATABASE_PASSWORD=DATABASE_PASSWORD,
        DATABASE_HOST=DATABASE_HOST,
        DATABASE_PORT=DATABASE_PORT,
        DATABASE_CONN_MAX_AGE=DATABASE_CONN_MAX_AGE,
        DATABASE_OPTIONS=DATABASE_OPTIONS.to_dict(),
        DEBUG=DEBUG,
        LOG_LEVEL=LOG_LEVEL,
        LOGGING=LOGGING,
        READ_LOGIN_REQUIRED=READ_LOGIN_REQUIRED,
        WRITE_LOGIN_REQUIRED=WRITE_LOGIN_REQUIRED,
        PAGE_SIZE=PAGE_SIZE,
        DISTRIBUTED_SQLITE=DISTRIBUTED_SQLITE,
        DISTRIBUTED_SQLITE_PREFIX=DISTRIBUTED_SQLITE_PREFIX,
        DISTRIBUTED_SQLITE_ROOT=DISTRIBUTED_SQLITE_ROOT,
        TIME_ZONE=TIME_ZONE,
    )
    with open(DEFAULT_SETTINGS, "w+") as settings_file:
        comment = textwrap.dedent(
            """
            ---
            # This is a default settings template generated by ARA.
            # To use a settings file such as this one, you need to export the
            # ARA_SETTINGS environment variable like so:
            #   $ export ARA_SETTINGS="{}"

            """.format(
                DEFAULT_SETTINGS
            )
        )
        print("[ara] Writing default settings to %s" % DEFAULT_SETTINGS)
        settings_file.write(comment.lstrip())
        yaml.dump({"default": SETTINGS}, settings_file)

if BASE_PATH:
    BASE_PATH = BASE_PATH.rstrip("/")
    if STATIC_URL.startswith("/") and not STATIC_URL.startswith("//"):
        STATIC_URL = BASE_PATH + STATIC_URL
