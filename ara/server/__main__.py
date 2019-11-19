#!/usr/bin/env python
#  Copyright (c) 2019 Red Hat, Inc.
#
#  This file is part of ARA Records Ansible.
#
#  ARA is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  ARA is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with ARA.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys

from django.conf import settings

from ara.setup.exceptions import MissingDjangoException, MissingMysqlclientException, MissingPsycopgException


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ara.server.settings")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as e:
        raise MissingDjangoException from e

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
    print("[ara] Using settings file: %s" % settings.ARA_SETTINGS)


if __name__ == "__main__":
    main()
