# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import threading

from django.db.backends.sqlite3.base import DatabaseWrapper as BaseDatabaseWrapper

local_storage = threading.local()


class DatabaseWrapper(BaseDatabaseWrapper):
    """
    Custom sqlite database backend meant to work with ara.server.wsgi.distributed_sqlite
    in order to dynamically load different databases at runtime.
    """

    def get_new_connection(self, conn_params):
        if hasattr(local_storage, "db_path") and local_storage.db_path:
            conn_params["database"] = local_storage.db_path
        return super().get_new_connection(conn_params)
