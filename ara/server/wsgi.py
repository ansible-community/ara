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

import logging
import os

from ara.setup.exceptions import MissingDjangoException

try:
    from django.core.wsgi import get_wsgi_application
    from django.core.handlers.wsgi import get_path_info, get_script_name
except ImportError as e:
    raise MissingDjangoException from e

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ara.server.settings")

logger = logging.getLogger(__name__)

# The default WSGI application
application = get_wsgi_application()


def handle_405(start_response):
    start_response("405 Method Not Allowed", [("content-type", "text/html")])
    return [b"<h1>Method Not Allowed</h1><p>This endpoint is read only.</p>"]


def handle_404(start_response):
    start_response("404 Not Found", [("content-type", "text/html")])
    return [b"<h1>Not Found</h1><p>The requested resource was not found on this server.</p>"]


def distributed_sqlite(environ, start_response):
    """
    Custom WSGI application meant to work with ara.server.db.backends.distributed_sqlite
    in order to dynamically load different databases at runtime.
    """
    # This endpoint is read only, do not accept write requests.
    if environ["REQUEST_METHOD"] not in ["GET", "HEAD", "OPTIONS"]:
        handle_405(start_response)

    script_name = get_script_name(environ)
    path_info = get_path_info(environ)

    from django.conf import settings

    # The root under which database files are expected
    root = settings.DISTRIBUTED_SQLITE_ROOT
    # The prefix after which everything should be delegated (ex: /ara-report)
    prefix = settings.DISTRIBUTED_SQLITE_PREFIX

    # Static assets should always be served by the regular app
    if path_info.startswith(settings.STATIC_URL):
        return application(environ, start_response)

    if prefix not in path_info:
        logger.warn("Ignoring request: URL does not contain delegated prefix (%s)" % prefix)
        return handle_404(start_response)

    # Slice path_info up until after the prefix to obtain the requested directory
    i = path_info.find(prefix) + len(prefix)
    fs_path = path_info[:i]

    # Make sure we aren't escaping outside the root and the directory exists
    db_dir = os.path.abspath(os.path.join(root, fs_path.lstrip("/")))
    if not db_dir.startswith(root):
        logger.warn("Ignoring request: path is outside the root (%s)" % db_dir)
        return handle_404(start_response)
    elif not os.path.exists(db_dir):
        logger.warn("Ignoring request: database directory not found (%s)" % db_dir)
        return handle_404(start_response)

    # Find the database file and make sure it exists
    db_file = os.path.join(db_dir, "ansible.sqlite")
    if not os.path.exists(db_file):
        logger.warn("Ignoring request: database file not found (%s)" % db_file)
        return handle_404(start_response)

    # Tell Django about the new URLs it should be using
    environ["SCRIPT_NAME"] = script_name + fs_path
    environ["PATH_INFO"] = path_info[len(fs_path) :]  # noqa: E203

    # Store the path of the database in a thread so the distributed_sqlite
    # database backend can retrieve it.
    from ara.server.db.backends.distributed_sqlite.base import local_storage

    local_storage.db_path = db_file
    try:
        return application(environ, start_response)
    finally:
        del local_storage.db_path
