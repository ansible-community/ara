#   Copyright 2017 Red Hat, Inc. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

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
