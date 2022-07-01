# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from requests.auth import HTTPBasicAuth


def get_client(
    client="offline",
    endpoint="http://127.0.0.1:8000",
    timeout=30,
    username=None,
    password=None,
    cert=None,
    key=None,
    verify=True,
    run_sql_migrations=True,
):
    """
    Returns a specified client configuration or one with sane defaults.
    """
    auth = None
    if username is not None and password is not None:
        auth = HTTPBasicAuth(username, password)

    cert = None
    if cert is not None and key is not None:
        cert = (cert, key)

    if client == "offline":
        from ara.clients.offline import AraOfflineClient

        return AraOfflineClient(auth=auth, run_sql_migrations=run_sql_migrations)
    elif client == "http":
        from ara.clients.http import AraHttpClient

        return AraHttpClient(endpoint=endpoint, timeout=timeout, auth=auth, cert=cert, verify=verify)
    else:
        raise ValueError("Unsupported API client: %s (use 'http' or 'offline')" % client)


def active_client():
    return active_client._instance()


active_client._instance = None
