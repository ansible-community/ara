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

import logging
import requests
from oslo_serialization import jsonutils
from ara.webapp import create_app
from flask import current_app

SUPPORTED_CLIENTS = ['python', 'http']


class AraHTTPClient(object):
    """
    Provides an interface to the REST API with a basic http client
    """
    def __init__(self, endpoint=None, timeout=15, **kwargs):
        self.log = logging.getLogger(current_app.logger_name)
        self.user_agent = 'ara-httpclient'
        if endpoint is None:
            endpoint = current_app.config['ARA_API_ENDPOINT']
        self.endpoint = endpoint
        self.timeout = timeout

        self.params = kwargs
        self.http = requests.Session()

    def _request(self, method, uri, **kwargs):
        if self.timeout is not None:
            kwargs.setdefault('timeout', self.timeout)

        kwargs.setdefault('headers', kwargs.get('headers', {}))
        kwargs['headers']['User-Agent'] = self.user_agent
        kwargs['headers']['Accept'] = 'application/json'
        kwargs['headers']['Content-Type'] = 'application/json'

        url = self.endpoint + uri
        self.log.debug('httpclient %s on %s' % (method, url))
        response = self.http.request(method, url, **kwargs)

        body = None
        if response.text:
            try:
                body = jsonutils.loads(response.text)
            except ValueError:
                pass

        return response, body

    def get(self, url, **kwargs):
        return self._request('GET', url, **kwargs)

    def post(self, url, **kwargs):
        return self._request('POST', url, **kwargs)

    def patch(self, url, **kwargs):
        return self._request('PATCH', url, **kwargs)

    def put(self, url, **kwargs):
        return self._request('PUT', url, **kwargs)

    def delete(self, url, **kwargs):
        return self._request('DELETE', url, **kwargs)


class AraPythonClient(object):
    """
    Provides a passthrough interface to the REST API with Flask's test_client
    """
    def __init__(self, **kwargs):
        self.client = current_app.test_client()
        self.log = logging.getLogger(current_app.logger_name)
        self.environ_base = dict(
            HTTP_USER_AGENT='ara-pythonclient',
            REMOTE_ADDR='127.0.0.1'
        )

    def _request(self, method, uri, **kwargs):
        self.log.debug('pythonclient %s on %s' % (method, uri))
        call = getattr(self.client, method)
        response = call(uri, environ_base=self.environ_base,
                        content_type='application/json', **kwargs)

        body = None
        if response.data:
            try:
                body = jsonutils.loads(response.data)
            except ValueError:
                pass
        return response, body

    def get(self, url, **kwargs):
        return self._request('get', url, **kwargs)

    def patch(self, url, **kwargs):
        return self._request('patch', url, **kwargs)

    def post(self, url, **kwargs):
        return self._request('post', url, **kwargs)

    def put(self, url, **kwargs):
        return self._request('put', url, **kwargs)

    def delete(self, url, **kwargs):
        return self._request('delete', url, **kwargs)


def get_client(client=None, **kwargs):
    if not current_app:
        app = create_app()
        context = app.app_context()
        context.push()

    if client is None:
        client = current_app.config['ARA_API_CLIENT']

    if client == 'http':
        return AraHTTPClient(**kwargs)
    elif client == 'python':
        return AraPythonClient(**kwargs)
    else:
        raise ValueError('Unsupported client: %s' % client)
