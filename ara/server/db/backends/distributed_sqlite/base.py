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
