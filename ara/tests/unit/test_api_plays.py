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

from ara.tests.unit.common import ansible_run
from ara.tests.unit.common import TestAra
from ara.api.plays import PlayApi
import ara.db.models as models
import pytest

from oslo_serialization import jsonutils
from werkzeug.routing import RequestRedirect


class TestApiPlays(TestAra):
    """ Tests for the ARA API interface """
    def setUp(self):
        super(TestApiPlays, self).setUp()

    def tearDown(self):
        super(TestApiPlays, self).tearDown()

    ###########
    # POST
    ###########
    def test_post_http_redirect(self):
        # TODO: Does this raise a RequestRedirect due to underlying 405 ?
        with pytest.raises(RequestRedirect):
            self.client.post('/api/v1/plays')

    # Not implemented yet
    def test_post_http_unimplemented(self):
        res = self.client.post('/api/v1/plays/')
        self.assertEqual(res.status_code, 405)

    def test_post_internal_unimplemented(self):
        http = self.client.post('/api/v1/plays/')
        internal = PlayApi().post()
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    ###########
    # PATCH
    ###########
    def test_patch_http_redirect(self):
        # TODO: Does this raise a RequestRedirect due to underlying 405 ?
        with pytest.raises(RequestRedirect):
            self.client.patch('/api/v1/plays')

    # Not implemented yet
    def test_patch_http_unimplemented(self):
        res = self.client.patch('/api/v1/plays/')
        self.assertEqual(res.status_code, 405)

    def test_patch_internal_unimplemented(self):
        http = self.client.patch('/api/v1/plays/')
        internal = PlayApi().patch()
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    ###########
    # PUT
    ###########
    def test_put_http_redirect(self):
        # TODO: Does this raise a RequestRedirect due to underlying 405 ?
        with pytest.raises(RequestRedirect):
            self.client.put('/api/v1/plays')

    # Not implemented yet
    def test_put_http_unimplemented(self):
        res = self.client.put('/api/v1/plays/')
        self.assertEqual(res.status_code, 405)

    def test_put_internal_unimplemented(self):
        http = self.client.put('/api/v1/plays/')
        internal = PlayApi().put()
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    ###########
    # DELETE
    ###########
    def test_delete_http_redirect(self):
        # TODO: Does this raise a RequestRedirect due to underlying 405 ?
        with pytest.raises(RequestRedirect):
            self.client.delete('/api/v1/plays')

    # Not implemented yet
    def test_delete_http_unimplemented(self):
        res = self.client.delete('/api/v1/plays/')
        self.assertEqual(res.status_code, 405)

    def test_delete_internal_unimplemented(self):
        http = self.client.delete('/api/v1/plays/')
        internal = PlayApi().delete()
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    ###########
    # GET
    ###########
    def test_get_http_redirect(self):
        res = self.client.get('/api/v1/plays')
        self.assertEqual(res.status_code, 301)

    def test_get_http_help(self):
        res = self.client.get('/api/v1/plays/',
                              query_string=dict(help=True))
        self.assertEqual(res.status_code, 200)
        # TODO: Improve this
        self.assertTrue(b'result_output' in res.data)
        self.assertTrue(b'query_parameters' in res.data)

    def test_get_internal_help(self):
        http = self.client.get('/api/v1/plays/',
                               query_string=dict(help=True))
        internal = PlayApi().get(help=True)
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    def test_get_http_with_bad_params_404_help(self):
        res = self.client.get('/api/v1/plays/',
                              query_string=dict(id=0))
        self.assertEqual(res.status_code, 404)
        # TODO: Improve this
        self.assertTrue(b'result_output' in res.data)
        self.assertTrue(b'query_parameters' in res.data)

    def test_get_internal_with_bad_params_404_help(self):
        http = self.client.get('/api/v1/plays/',
                               query_string=dict(id=0))
        internal = PlayApi().get(id=0)
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    def test_get_http_without_parameters_and_data(self):
        res = self.client.get('/api/v1/plays/')
        self.assertEqual(res.status_code, 404)
        # TODO: Improve this
        self.assertTrue(b'result_output' in res.data)
        self.assertTrue(b'query_parameters' in res.data)

    def test_get_internal_without_parameters_and_data(self):
        http = self.client.get('/api/v1/plays/')
        internal = PlayApi().get()
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    def test_get_http_without_parameters(self):
        ctx = ansible_run()
        res = self.client.get('/api/v1/plays/')
        self.assertEqual(res.status_code, 200)

        data = jsonutils.loads(res.data)[0]

        self.assertEqual(ctx['play'].id,
                         data['id'])
        self.assertEqual(ctx['play'].playbook_id,
                         data['playbook_id'])
        self.assertEqual(ctx['play'].name,
                         data['name'])
        self.assertEqual(ctx['play'].started.isoformat(),
                         data['started'])
        self.assertEqual(ctx['play'].ended.isoformat(),
                         data['ended'])
        self.assertEqual(len(ctx['play'].results.all()),
                         len(data['results']))
        self.assertEqual(len(ctx['play'].tasks.all()),
                         len(data['tasks']))

    def test_get_internal_without_parameters(self):
        ansible_run()
        http = self.client.get('/api/v1/plays/')
        internal = PlayApi().get()
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    def test_get_http_with_id_parameter(self):
        ctx = ansible_run()
        # Run twice to get a second playbook
        ansible_run()
        playbooks = models.Playbook.query.all()
        self.assertEqual(len(playbooks), 2)

        res = self.client.get('/api/v1/plays/', query_string=dict(id=1))
        self.assertEqual(res.status_code, 200)

        data = jsonutils.loads(res.data)
        self.assertEqual(ctx['play'].id,
                         data['id'])
        self.assertEqual(ctx['play'].playbook_id,
                         data['playbook_id'])
        self.assertEqual(ctx['play'].name,
                         data['name'])
        self.assertEqual(ctx['play'].started.isoformat(),
                         data['started'])
        self.assertEqual(ctx['play'].ended.isoformat(),
                         data['ended'])
        self.assertEqual(len(ctx['play'].results.all()),
                         len(data['results']))
        self.assertEqual(len(ctx['play'].tasks.all()),
                         len(data['tasks']))

    def test_get_internal_with_id_parameter(self):
        ansible_run()
        # Run twice to get a second playbook
        ansible_run()
        playbooks = models.Playbook.query.all()
        self.assertEqual(len(playbooks), 2)

        http = self.client.get('/api/v1/plays/', query_string=dict(id=1))
        internal = PlayApi().get(id=1)
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    def test_get_http_with_id_url(self):
        ctx = ansible_run()
        # Run twice to get a second playbook
        ansible_run()
        playbooks = models.Playbook.query.all()
        self.assertEqual(len(playbooks), 2)

        res = self.client.get('/api/v1/plays/1')
        self.assertEqual(res.status_code, 200)

        data = jsonutils.loads(res.data)
        self.assertEqual(ctx['play'].id,
                         data['id'])
        self.assertEqual(ctx['play'].playbook_id,
                         data['playbook_id'])
        self.assertEqual(ctx['play'].name,
                         data['name'])
        self.assertEqual(ctx['play'].started.isoformat(),
                         data['started'])
        self.assertEqual(ctx['play'].ended.isoformat(),
                         data['ended'])
        self.assertEqual(len(ctx['play'].results.all()),
                         len(data['results']))
        self.assertEqual(len(ctx['play'].tasks.all()),
                         len(data['tasks']))

    def test_get_internal_with_id_url(self):
        ansible_run()
        # Run twice to get a second playbook
        ansible_run()
        playbooks = models.Playbook.query.all()
        self.assertEqual(len(playbooks), 2)

        http = self.client.get('/api/v1/plays/1')
        internal = PlayApi().get(id=1)
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)
