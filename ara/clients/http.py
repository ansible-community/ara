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
import requests


class HttpClient(object):
    def __init__(self, endpoint='http://127.0.0.1:8000', timeout=30, **params):
        self.endpoint = endpoint
        self.timeout = timeout
        self.params = params

        self.log = logging.getLogger(__name__)
        self.user_agent = 'ara-http-client'
        self.log.debug("%s: %s" % (self.user_agent, str(self.params)))

        self.http = requests.Session()

    def _request(self, method, url, **kwargs):
        # Override timeout and headers only if user supplied
        kwargs.setdefault('timeout', self.timeout)
        kwargs.setdefault('headers', kwargs.get('headers', {}))

        # Headers we're enforcing (kind of)
        kwargs['headers']['User-Agent'] = self.user_agent
        kwargs['headers']['Accept'] = 'application/json'
        kwargs['headers']['Content-Type'] = 'application/json'

        self.log.debug("%s on %s" % (method, url))

        # Use requests.Session to do the query
        # The actual endpoint is:
        # <endpoint>              <url>
        # http://127.0.0.1:8000 / api/v1/playbooks
        return self.http.request(method, self.endpoint + url, **kwargs)

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


class AraHttpClient(object):
    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.client = HttpClient()

    def _request(self, method, url, **kwargs):
        func = getattr(self.client, method)
        # TODO: Is there a better way than doing this if/else ?
        if kwargs:
            response = func(url, json.dumps(kwargs))
        else:
            response = func(url)

        if response.status_code >= 500:
            self.log.error(
                'Failed to {method} on {url}: {content}'.format(
                    method=method,
                    url=url,
                    content=kwargs
                )
            )

        self.log.debug('HTTP {status}: {method} on {url}'.format(
            status=response.status_code,
            method=method,
            url=url
        ))

        if response.status_code not in [200, 201, 204]:
            self.log.error(
                'Failed to {method} on {url}: {content}'.format(
                    method=method,
                    url=url,
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
