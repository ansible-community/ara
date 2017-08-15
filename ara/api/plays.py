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

from ara.webapp import create_app
from flask import current_app
from oslo_serialization import jsonutils


class PlayApi(object):
    """
    Internal API passthrough to the REST API: api.v1.plays
    """
    def __init__(self):
        if not current_app:
            app = create_app()
            self.context = app.app_context()
            self.context.push()

        self.client = current_app.test_client()

    def get(self, **kwargs):
        get = self.client.get('/api/v1/plays/',
                              content_type='application/json',
                              query_string=kwargs)
        return get

    def patch(self, data=None):
        patch = self.client.patch('/api/v1/plays/',
                                  content_type='application/json',
                                  data=jsonutils.dumps(data))
        return patch

    def post(self, data=None):
        post = self.client.post('/api/v1/plays/',
                                content_type='application/json',
                                data=jsonutils.dumps(data))
        return post

    def put(self, **kwargs):
        put = self.client.put('/api/v1/plays/', data=kwargs)
        return put

    def delete(self, **kwargs):
        delete = self.client.delete('/api/v1/plays/', data=kwargs)
        return delete
