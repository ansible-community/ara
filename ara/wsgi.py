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

# WSGI file to run the ARA server.
# It is expected that the server at least passes an ANSIBLE_CONFIG environment
# variable in order to configure Ansible and ARA.

# Can be configured using environment variables (i.e, Apache SetEnv) with the
# following variables:

# ARA_WSGI_USE_VIRTUALENV
#   Enable virtual environment usage if ARA is installed in a virtual
#   environment.
#   Defaults to '0', set to '1' to enable.
# ARA_WSGI_VIRTUALENV_PATH
#   When using a virtual environment, where the virtualenv is located.
#   Defaults to None, set to the absolute path of your virtualenv.

import os
import logging
import six
import threading

app = None
app_making_lock = threading.Lock()
log = logging.getLogger(__name__)


def application(environ, start_response):
    global app

    # Load virtualenv if necessary
    if (int(environ.get('ARA_WSGI_USE_VIRTUALENV', 0)) == 1 and
       environ.get('ARA_WSGI_VIRTUALENV_PATH')):
        # Backwards compatibility, we did not always suffix activate_this.py
        activate_this = environ.get('ARA_WSGI_VIRTUALENV_PATH')
        if 'activate_this.py' not in activate_this:
            activate_this = os.path.join(activate_this, 'bin/activate_this.py')
        if six.PY2:
            execfile(activate_this, dict(__file__=activate_this))  # nosec
        else:
            exec(open(activate_this).read())  # nosec

    if 'ANSIBLE_CONFIG' in environ:
        os.environ['ANSIBLE_CONFIG'] = environ['ANSIBLE_CONFIG']
    else:
        if 'ANSIBLE_CONFIG' not in os.environ:
            log.warn('ANSIBLE_CONFIG environment variable not found.')

    from ara.webapp import create_app  # flake8: noqa
    from flask import current_app  # flake8: noqa
    with app_making_lock:
        if app is None:
            app = create_app()
    with app.app_context():
        return current_app(environ, start_response)


def main():
    return application
