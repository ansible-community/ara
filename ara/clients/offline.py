#  Copyright (c) 2018 Red Hat, Inc.
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

# This is an "offline" API client that does not require standing up
# an API server and does not execute actual HTTP calls.

import json
import logging
import os


class AraOfflineClient(object):
    def __init__(self):
        self.log = logging.getLogger(__name__)

        try:
            from django import setup as django_setup
            from django.core.management import execute_from_command_line
            from django.test import Client

            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ara.server.settings')

            # Automatically create the database and run migrations (is there a better way?)
            execute_from_command_line(['django', 'migrate'])

            # Set up the things Django needs
            django_setup()
        except ImportError as e:
            self.log.error('The offline client requires ara-server to be installed')
            raise e

        self.client = Client()

    def _request(self, method, endpoint, **kwargs):
        func = getattr(self.client, method)
        # TODO: Is there a better way than doing this if/else ?
        if kwargs:
            response = func(
                endpoint,
                json.dumps(kwargs),
                content_type='application/json'
            )
        else:
            response = func(
                endpoint,
                content_type='application/json'
            )

        if response.status_code >= 500:
            self.log.error(
                'Failed to {method} on {endpoint}: {content}'.format(
                    method=method,
                    endpoint=endpoint,
                    content=kwargs
                )
            )

        self.log.debug('HTTP {status}: {method} on {endpoint}'.format(
            status=response.status_code,
            method=method,
            endpoint=endpoint
        ))

        if response.status_code not in [200, 201, 204]:
            self.log.error(
                'Failed to {method} on {endpoint}: {content}'.format(
                    method=method,
                    endpoint=endpoint,
                    content=kwargs
                )
            )

        if response.status_code == 204:
            return response

        return response.json()

    def get(self, endpoint, **kwargs):
        return self._request('get', endpoint, **kwargs)

    def patch(self, endpoint, **kwargs):
        return self._request('patch', endpoint, **kwargs)

    def post(self, endpoint, **kwargs):
        return self._request('post', endpoint, **kwargs)

    def put(self, endpoint, **kwargs):
        return self._request('put', endpoint, **kwargs)

    def delete(self, endpoint, **kwargs):
        return self._request('delete', endpoint, **kwargs)
