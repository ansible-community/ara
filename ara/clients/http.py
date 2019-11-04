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
import weakref

import pbr.version
import requests

from ara.clients.utils import active_client

CLIENT_VERSION = pbr.version.VersionInfo("ara").release_string()


class HttpClient(object):
    def __init__(self, endpoint="http://127.0.0.1:8000", auth=None, timeout=30, verify=True):
        self.log = logging.getLogger(__name__)

        self.endpoint = endpoint.rstrip("/")
        self.auth = auth
        self.timeout = timeout
        self.verify = verify
        self.headers = {
            "User-Agent": "ara-http-client_%s" % CLIENT_VERSION,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        self.http = requests.Session()
        self.http.headers.update(self.headers)
        if self.auth is not None:
            self.http.auth = self.auth
        self.http.verify = self.verify

    def _request(self, method, url, **payload):
        # Use requests.Session to do the query
        # The actual endpoint is:
        # <endpoint>              <url>
        # http://127.0.0.1:8000 / api/v1/playbooks
        return self.http.request(method, self.endpoint + url, timeout=self.timeout, **payload)

    def get(self, url, **payload):
        if payload:
            return self._request("get", url, **payload)
        else:
            return self._request("get", url)

    def patch(self, url, **payload):
        return self._request("patch", url, data=json.dumps(payload))

    def post(self, url, **payload):
        return self._request("post", url, data=json.dumps(payload))

    def put(self, url, **payload):
        return self._request("put", url, data=json.dumps(payload))

    def delete(self, url):
        return self._request("delete", url)


class AraHttpClient(object):
    def __init__(self, endpoint="http://127.0.0.1:8000", auth=None, timeout=30, verify=True):
        self.log = logging.getLogger(__name__)
        self.endpoint = endpoint
        self.auth = auth
        self.timeout = timeout
        self.verify = verify
        self.client = HttpClient(endpoint=self.endpoint, timeout=self.timeout, auth=self.auth, verify=self.verify)
        active_client._instance = weakref.ref(self)

    def _request(self, method, url, **kwargs):
        func = getattr(self.client, method)
        if method == "delete":
            response = func(url)
        else:
            response = func(url, **kwargs)

        if response.status_code >= 500:
            self.log.error("Failed to {method} on {url}: {content}".format(method=method, url=url, content=kwargs))

        self.log.debug("HTTP {status}: {method} on {url}".format(status=response.status_code, method=method, url=url))

        if response.status_code not in [200, 201, 204]:
            self.log.error("Failed to {method} on {url}: {content}".format(method=method, url=url, content=kwargs))

        if response.status_code == 204:
            return response

        return response.json()

    def get(self, endpoint, **kwargs):
        return self._request("get", endpoint, params=kwargs)

    def patch(self, endpoint, **kwargs):
        return self._request("patch", endpoint, **kwargs)

    def post(self, endpoint, **kwargs):
        return self._request("post", endpoint, **kwargs)

    def put(self, endpoint, **kwargs):
        return self._request("put", endpoint, **kwargs)

    def delete(self, endpoint, **kwargs):
        return self._request("delete", endpoint)
