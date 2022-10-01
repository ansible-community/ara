# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json
import logging
import weakref

import requests
import urllib3

from ara.clients.utils import active_client
from ara.setup import ara_version


class HttpClient:
    def __init__(self, endpoint="http://127.0.0.1:8000", auth=None, cert=None, timeout=30, verify=True):
        self.log = logging.getLogger(__name__)

        self.endpoint = endpoint.rstrip("/")
        self.auth = auth
        self.cert = cert
        self.timeout = int(timeout)
        self.verify = verify
        self.headers = {
            "User-Agent": "ara-http-client_%s" % ara_version,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        self.http = requests.Session()
        self.http.headers.update(self.headers)
        if self.auth is not None:
            self.http.auth = self.auth
        if self.cert is not None:
            self.http.cert = self.cert
        if not self.verify:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
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


class AraHttpClient:
    def __init__(self, endpoint="http://127.0.0.1:8000", auth=None, cert=None, timeout=30, verify=True):
        self.log = logging.getLogger(__name__)
        self.endpoint = endpoint
        self.auth = auth
        self.cert = cert
        self.timeout = int(timeout)
        self.verify = verify
        self.client = HttpClient(
            endpoint=self.endpoint, timeout=self.timeout, auth=self.auth, cert=self.cert, verify=self.verify
        )
        active_client._instance = weakref.ref(self)

    def _request(self, method, url, **kwargs):
        func = getattr(self.client, method)
        if method == "delete":
            response = func(url)
        else:
            response = func(url, **kwargs)

        if response.status_code >= 500:
            self.log.error(f"Failed to {method} on {url}: {kwargs}")

        self.log.debug(f"HTTP {response.status_code}: {method} on {url}")

        if response.status_code not in [200, 201, 204]:
            self.log.error(f"Failed to {method} on {url}: {kwargs}")

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
