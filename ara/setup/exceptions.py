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


class MissingDjangoException(Exception):
    def __init__(self):
        exc = "The server dependencies must be installed to record data offline or run the API server."
        super().__init__(exc)


class MissingPsycopgException(Exception):
    def __init__(self):
        exc = "The psycopg2 python library must be installed in order to use the PostgreSQL database engine."
        super().__init__(exc)


class MissingMysqlclientException(Exception):
    def __init__(self):
        exc = "The mysqlclient python library must be installed in order to use the MySQL database engine."
        super().__init__(exc)


class MissingSettingsException(Exception):
    def __init__(self):
        exc = "The specified settings file does not exist or permissions are insufficient to read it."
        super().__init__(exc)
