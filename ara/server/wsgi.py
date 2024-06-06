# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
import os

from ara.setup.exceptions import MissingDjangoException

try:
    from django.conf import settings
    from django.core.handlers.wsgi import get_path_info, get_script_name
    from django.core.wsgi import get_wsgi_application
except ImportError as e:
    raise MissingDjangoException from e

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ara.server.settings")

logger = logging.getLogger(__name__)

# The default WSGI application
default_application = get_wsgi_application()


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
        return handle_405(start_response)

    script_name = get_script_name(environ)
    original_path_info = get_path_info(environ)

    prefix_len = len(settings.BASE_PATH)
    if len(original_path_info) < prefix_len:
        return handle_404(start_response)

    path_info = original_path_info[prefix_len:]
    # The root under which database files are expected
    root = settings.DISTRIBUTED_SQLITE_ROOT
    # The prefix after which everything should be delegated (ex: /ara-report)
    prefix = settings.DISTRIBUTED_SQLITE_PREFIX

    # Static assets and healthcheck should always be served by the regular app
    if original_path_info.startswith(settings.STATIC_URL) or path_info == "/healthcheck/":
        return default_application(environ, start_response)

    # The root of the application should be served by the regular app to show
    # a distributed database index
    if path_info == "" or path_info == "/":
        environ["SCRIPT_NAME"] = settings.BASE_PATH
        environ["PATH_INFO"] = "/distributed"
        return default_application(environ, start_response)

    if prefix not in path_info:
        logger.warning("Ignoring request: URL does not contain delegated prefix (%s)" % prefix)
        return handle_404(start_response)

    # Slice path_info up until after the prefix to obtain the requested directory
    i = path_info.find(prefix) + len(prefix)
    fs_path = path_info[:i]

    # Make sure we aren't escaping outside the root and the directory exists
    db_dir = os.path.abspath(os.path.join(root, fs_path.lstrip("/")))
    if not db_dir.startswith(root):
        logger.warning("Ignoring request: path is outside the root (%s)" % db_dir)
        return handle_404(start_response)
    elif not os.path.exists(db_dir):
        logger.warning("Ignoring request: database directory not found (%s)" % db_dir)
        return handle_404(start_response)

    # Find the database file and make sure it exists
    db_file = os.path.join(db_dir, "ansible.sqlite")
    if not os.path.exists(db_file):
        logger.warning("Ignoring request: database file not found (%s)" % db_file)
        return handle_404(start_response)

    # Tell Django about the new URLs it should be using
    environ["SCRIPT_NAME"] = settings.BASE_PATH + script_name + fs_path
    environ["PATH_INFO"] = path_info[len(fs_path) :]  # noqa: E203

    # Store the path of the database in a thread so the distributed_sqlite
    # database backend can retrieve it.
    from ara.server.db.backends.distributed_sqlite.base import local_storage

    local_storage.db_path = db_file
    try:
        return default_application(environ, start_response)
    finally:
        del local_storage.db_path


application = distributed_sqlite if settings.DISTRIBUTED_SQLITE else default_application
