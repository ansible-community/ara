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


class ResultApi(object):
    """
    Internal API passthrough to the REST API: api.v1.results
    """
    def __init__(self):
        if not current_app:
            app = create_app()
            self.context = app.app_context()
            self.context.push()

        self.client = current_app.test_client()

    def get(self, **kwargs):
        data = self.client.get('/api/v1/results', query_string=kwargs)
        return data

    def post(self, **kwargs):
        data = self.client.post('/api/v1/results', data=kwargs)
        return data

    def put(self, **kwargs):
        data = self.client.put('/api/v1/results', data=kwargs)
        return data

    def delete(self, **kwargs):
        data = self.client.delete('/api/v1/results', data=kwargs)
        return data
