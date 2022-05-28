# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
import os
import threading

from ara.clients.http import AraHttpClient
from ara.setup.exceptions import MissingDjangoException

try:
    from django.core.handlers.wsgi import WSGIHandler
    from django.core.servers.basehttp import ThreadedWSGIServer, WSGIRequestHandler
except ImportError as e:
    raise MissingDjangoException from e


class AraOfflineClient(AraHttpClient):
    def __init__(self, auth=None, run_sql_migrations=True):
        self.log = logging.getLogger(__name__)

        from django import setup as django_setup
        from django.core.management import execute_from_command_line

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ara.server.settings")

        if run_sql_migrations:
            # Automatically create the database and run migrations (is there a better way?)
            execute_from_command_line(["django", "migrate"])

        # Set up the things Django needs
        django_setup()

        self._start_server()
        super().__init__(endpoint="http://localhost:%d" % self.server_thread.port, auth=auth)

    def _start_server(self):
        self.server_thread = ServerThread("localhost")
        self.server_thread.start()

        # Wait for the live server to be ready
        self.server_thread.is_ready.wait()
        if self.server_thread.error:
            raise self.server_thread.error


class ServerThread(threading.Thread):
    def __init__(self, host, port=0):
        self.host = host
        self.port = port
        self.is_ready = threading.Event()
        self.error = None
        super().__init__(daemon=True)

    def run(self):
        """
        Set up the live server and databases, and then loop over handling
        HTTP requests.
        """
        try:
            # Create the handler for serving static and media files
            self.httpd = self._create_server()
            # If binding to port zero, assign the port allocated by the OS.
            if self.port == 0:
                self.port = self.httpd.server_address[1]
            self.httpd.set_app(WSGIHandler())
            self.is_ready.set()
            self.httpd.serve_forever()
        except Exception as e:
            self.error = e
            self.is_ready.set()

    def _create_server(self):
        return ThreadedWSGIServer((self.host, self.port), QuietWSGIRequestHandler, allow_reuse_address=False)


class QuietWSGIRequestHandler(WSGIRequestHandler):
    def log_message(*args):
        pass
