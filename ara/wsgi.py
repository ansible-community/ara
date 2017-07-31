#  Copyright (c) 2017 Red Hat, Inc.
#
#  This file is part of ARA: Ansible Run Analysis.
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


def application(environ, start_response):
    os.environ['ANSIBLE_CONFIG'] = environ['ANSIBLE_CONFIG']
    from ara.webapp import create_app
    app = create_app()
    return app(environ, start_response)


def main():
    return application
