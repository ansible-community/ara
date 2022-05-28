#!/usr/bin/env python3
# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import sys

from django.conf import settings

from ara.setup.exceptions import (
    MissingDjangoException,
    MissingMysqlclientException,
    MissingPsycopgException,
    MissingSettingsException,
)


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ara.server.settings")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as e:
        raise MissingDjangoException from e

    # Validate that the settings file exists and is readable before bootstrapping
    if not os.path.exists(settings.ARA_SETTINGS):
        print("[ara] Unable to access or read settings file: %s" % settings.ARA_SETTINGS)
        raise MissingSettingsException
    print("[ara] Using settings file: %s" % settings.ARA_SETTINGS)

    if settings.DATABASE_ENGINE == "django.db.backends.postgresql":
        try:
            import psycopg2  # noqa
        except ImportError as e:
            raise MissingPsycopgException from e

    if settings.DATABASE_ENGINE == "django.db.backends.mysql":
        try:
            import MySQLdb  # noqa
        except ImportError as e:
            raise MissingMysqlclientException from e

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
