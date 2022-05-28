# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


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
