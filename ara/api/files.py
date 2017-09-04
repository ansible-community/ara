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

from ara.api.client import get_client
from oslo_serialization import jsonutils


class FileApi(object):
    """
    Internal API passthrough to the REST API: api.v1.files
    """
    def __init__(self, client=None):
        self.client = get_client(client)
        self.endpoint = '/api/v1/files/'

    def get(self, **kwargs):
        return self.client.get(self.endpoint, query_string=kwargs)

    def patch(self, **kwargs):
        return self.client.patch(self.endpoint, data=jsonutils.dumps(kwargs))

    def post(self, **kwargs):
        return self.client.post(self.endpoint, data=jsonutils.dumps(kwargs))

    def put(self, **kwargs):
        return self.client.put(self.endpoint, data=jsonutils.dumps(kwargs))

    def delete(self, **kwargs):
        return self.client.delete(self.endpoint, data=jsonutils.dumps(kwargs))
