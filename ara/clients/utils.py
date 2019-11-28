#  Copyright (c) 2018 Red Hat, Inc.
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

from requests.auth import HTTPBasicAuth


def get_client(
    client="offline",
    endpoint="http://127.0.0.1:8000",
    timeout=30,
    username=None,
    password=None,
    verify=True,
    run_sql_migrations=True,
):
    """
    Returns a specified client configuration or one with sane defaults.
    """
    auth = None
    if username is not None and password is not None:
        auth = HTTPBasicAuth(username, password)

    if client == "offline":
        from ara.clients.offline import AraOfflineClient

        return AraOfflineClient(auth=auth, run_sql_migrations=run_sql_migrations)
    elif client == "http":
        from ara.clients.http import AraHttpClient

        return AraHttpClient(endpoint=endpoint, timeout=timeout, auth=auth, verify=verify)
    else:
        raise ValueError("Unsupported API client: %s (use 'http' or 'offline')" % client)


def active_client():
    return active_client._instance()


active_client._instance = None
