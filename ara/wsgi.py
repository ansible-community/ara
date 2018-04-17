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

# WSGI file to run the ARA server, it is expected that the server passes an
# ANSIBLE_CONFIG environment variable in order to configure Ansible and ARA.

import os
import logging

from ara.webapp import create_app
from flask import current_app

log = logging.getLogger(__name__)
app = create_app()


def application(environ, start_response):
    if 'ANSIBLE_CONFIG' in environ:
        os.environ['ANSIBLE_CONFIG'] = environ['ANSIBLE_CONFIG']
    else:
        if 'ANSIBLE_CONFIG' not in os.environ:
            log.warn('ANSIBLE_CONFIG environment variable not found.')

    if not current_app:
        ctx = app.app_context()
        ctx.push()
        return app(environ, start_response)
    else:
        return current_app(environ, start_response)


def main():
    return application
