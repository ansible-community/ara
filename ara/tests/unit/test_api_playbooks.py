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
from ara.api.playbooks import PlaybookApi
import ara.db.models as models
import pytest

from oslo_serialization import jsonutils
from werkzeug.routing import RequestRedirect


class TestApiPlaybooks(TestAra):
    """ Tests for the ARA API interface """
    def setUp(self):
        super(TestApiPlaybooks, self).setUp()

    def tearDown(self):
        super(TestApiPlaybooks, self).tearDown()

    ###########
    # POST
    ###########
    def test_post_http_redirect(self):
        res = self.client.post('/api/v1/playbooks')
        self.assertEqual(res.status_code, 301)

    def test_post_http_with_correct_data(self):
        data = {
            "path": "/root/playbook.yml",
            "ansible_version": "2.2.3.1",
            "parameters": {
                "become": False,
                "become_user": "root"
            },
            "completed": False,
            "started": "1970-08-14T00:52:49.570031"
        }
        res = self.client.post('/api/v1/playbooks/',
                               data=jsonutils.dumps(data),
                               content_type='application/json')
        self.assertEqual(res.status_code, 201)
        data = jsonutils.loads(res.data)[0]

        playbook = models.Playbook.query.get(data['id'])
        self.assertIsNotNone(playbook)
        self.assertEquals(data['id'], playbook.id)
        self.assertEquals(data['path'], playbook.path)
        self.assertEquals(data['ansible_version'], playbook.ansible_version)
        self.assertEquals(data['parameters'], playbook.parameters)
        self.assertEquals(data['completed'], playbook.completed)
        self.assertEquals(data['started'], playbook.started.isoformat())
        self.assertEquals(data['ended'], playbook.ended)

    def test_post_internal_with_correct_data(self):
        data = {
            "path": "/root/playbook.yml",
            "ansible_version": "2.2.3.1",
            "parameters": {
                "become": False,
                "become_user": "root"
            },
            "completed": False,
            "started": "1970-08-14T00:52:49.570031"
        }
        res = PlaybookApi().post(data)

        self.assertEqual(res.status_code, 201)
        data = jsonutils.loads(res.data)[0]

        playbook = models.Playbook.query.get(data['id'])
        self.assertIsNotNone(playbook)
        self.assertEquals(data['id'], playbook.id)
        self.assertEquals(data['path'], playbook.path)
        self.assertEquals(data['ansible_version'], playbook.ansible_version)
        self.assertEquals(data['parameters'], playbook.parameters)
        self.assertEquals(data['completed'], playbook.completed)
        self.assertEquals(data['started'], playbook.started.isoformat())
        self.assertEquals(data['ended'], playbook.ended)

    def test_post_http_with_incorrect_data(self):
        data = {
            "path": False,
            "ansible_version": 2,
            "parameters": ['one'],
            "completed": "yes",
            "started": "a long time ago"
        }

        res = self.client.post('/api/v1/playbooks/',
                               data=jsonutils.dumps(data),
                               content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_post_internal_with_incorrect_data(self):
        data = {
            "path": False,
            "ansible_version": 2,
            "parameters": ['one'],
            "completed": "yes",
            "started": "a long time ago"
        }

        res = PlaybookApi().post(data)
        self.assertEqual(res.status_code, 400)

    def test_post_http_with_missing_argument(self):
        data = {
            "path": "/root/playbook.yml",
        }
        res = self.client.post('/api/v1/playbooks/',
                               data=jsonutils.dumps(data),
                               content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_post_internal_with_missing_argument(self):
        data = {
            "path": "/root/playbook.yml",
        }
        res = PlaybookApi().post(data)
        self.assertEqual(res.status_code, 400)

    ###########
    # PATCH
    ###########
    def test_patch_http_redirect(self):
        res = self.client.patch('/api/v1/playbooks')
        self.assertEqual(res.status_code, 301)

    def test_patch_http_existing(self):
        ctx = ansible_run()
        new_version = "1.9.9.6"
        self.assertEquals(ctx['playbook'].id, 1)
        self.assertNotEquals(ctx['playbook'].ansible_version,
                             new_version)

        data = {
            "id": ctx['playbook'].id,
            "ansible_version": new_version
        }

        res = self.client.patch('/api/v1/playbooks/',
                                data=jsonutils.dumps(data),
                                content_type='application/json')
        self.assertEquals(res.status_code, 200)
        data = jsonutils.loads(res.data)[0]

        self.assertEquals(data['ansible_version'],
                          new_version)

        # Confirm by re-fetching playbook
        updated = self.client.get('/api/v1/playbooks/',
                                  query_string=dict(id=ctx['playbook'].id))
        updated_playbook = jsonutils.loads(updated.data)
        self.assertEquals(updated_playbook['ansible_version'],
                          new_version)

    def test_patch_internal_existing(self):
        ctx = ansible_run()
        new_version = "1.9.9.6"
        self.assertEquals(ctx['playbook'].id, 1)
        self.assertNotEquals(ctx['playbook'].ansible_version,
                             new_version)

        data = {
            "id": ctx['playbook'].id,
            "ansible_version": new_version
        }

        res = PlaybookApi().patch(data)
        self.assertEquals(res.status_code, 200)
        data = jsonutils.loads(res.data)[0]

        self.assertEquals(data['ansible_version'],
                          new_version)

        # Confirm by re-fetching playbook
        updated = PlaybookApi().get(
            query_string=dict(id=ctx['playbook'].id)
        )
        updated_playbook = jsonutils.loads(updated.data)[0]
        self.assertEquals(updated_playbook['ansible_version'],
                          new_version)

    def test_patch_http_with_missing_arg(self):
        ansible_run()
        data = {
            "ansible_version": "1.9.9.6"
        }
        res = self.client.patch('/api/v1/playbooks/',
                                data=jsonutils.dumps(data),
                                content_type='application/json')
        self.assertEquals(res.status_code, 400)

    def test_patch_internal_with_missing_arg(self):
        ansible_run()
        data = {
            "ansible_version": "1.9.9.6"
        }
        res = PlaybookApi().patch(data)
        self.assertEquals(res.status_code, 400)

    ###########
    # PUT
    ###########
    def test_put_http_redirect(self):
        # TODO: Does this raise a RequestRedirect due to underlying 405 ?
        with pytest.raises(RequestRedirect):
            self.client.put('/api/v1/playbooks')

    # Not implemented yet
    def test_put_http_unimplemented(self):
        res = self.client.put('/api/v1/playbooks/')
        self.assertEqual(res.status_code, 405)

    def test_put_internal_unimplemented(self):
        http = self.client.put('/api/v1/playbooks/')
        internal = PlaybookApi().put()
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    ###########
    # DELETE
    ###########
    def test_delete_http_redirect(self):
        # TODO: Does this raise a RequestRedirect due to underlying 405 ?
        with pytest.raises(RequestRedirect):
            self.client.delete('/api/v1/playbooks')

    # Not implemented yet
    def test_delete_http_unimplemented(self):
        res = self.client.delete('/api/v1/playbooks/')
        self.assertEqual(res.status_code, 405)

    def test_delete_internal_unimplemented(self):
        http = self.client.delete('/api/v1/playbooks/')
        internal = PlaybookApi().delete()
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    ###########
    # GET
    ###########
    def test_get_http_redirect(self):
        res = self.client.get('/api/v1/playbooks')
        self.assertEqual(res.status_code, 301)

    def test_get_http_help(self):
        res = self.client.get('/api/v1/playbooks/',
                              query_string=dict(help=True))
        self.assertEqual(res.status_code, 200)
        # TODO: Improve this
        self.assertTrue(b'result_output' in res.data)
        self.assertTrue(b'query_parameters' in res.data)

    def test_get_internal_help(self):
        http = self.client.get('/api/v1/playbooks/',
                               query_string=dict(help=True))
        internal = PlaybookApi().get(help=True)
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    def test_get_http_with_bad_params_404_help(self):
        res = self.client.get('/api/v1/playbooks/',
                              query_string=dict(id=0))
        self.assertEqual(res.status_code, 404)
        # TODO: Improve this
        self.assertTrue(b'result_output' in res.data)
        self.assertTrue(b'query_parameters' in res.data)

    def test_get_internal_with_bad_params_404_help(self):
        http = self.client.get('/api/v1/playbooks/',
                               query_string=dict(id=0))
        internal = PlaybookApi().get(id=0)
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    def test_get_http_without_parameters_and_data(self):
        res = self.client.get('/api/v1/playbooks/')
        self.assertEqual(res.status_code, 404)
        # TODO: Improve this
        self.assertTrue(b'result_output' in res.data)
        self.assertTrue(b'query_parameters' in res.data)

    def test_get_internal_without_parameters_and_data(self):
        http = self.client.get('/api/v1/playbooks/')
        internal = PlaybookApi().get()
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    def test_get_http_without_parameters(self):
        ctx = ansible_run()
        res = self.client.get('/api/v1/playbooks/')
        self.assertEqual(res.status_code, 200)

        data = jsonutils.loads(res.data)[0]

        self.assertEqual(ctx['playbook'].id,
                         data['id'])
        self.assertEqual(ctx['playbook'].path,
                         data['path'])
        self.assertEqual(ctx['playbook'].completed,
                         data['completed'])
        self.assertEqual(ctx['playbook'].started.isoformat(),
                         data['started'])
        self.assertEqual(ctx['playbook'].ended.isoformat(),
                         data['ended'])
        self.assertEqual(ctx['playbook'].parameters,
                         data['parameters'])
        self.assertEqual(ctx['playbook'].ansible_version,
                         data['ansible_version'])
        self.assertEqual(len(ctx['playbook'].files.all()),
                         len(data['files']))
        self.assertEqual(len(ctx['playbook'].hosts.all()),
                         len(data['hosts']))
        self.assertEqual(len(ctx['playbook'].plays.all()),
                         len(data['plays']))
        self.assertEqual(len(ctx['playbook'].results.all()),
                         len(data['results']))
        self.assertEqual(len(ctx['playbook'].tasks.all()),
                         len(data['tasks']))

    def test_get_internal_without_parameters(self):
        ansible_run()
        http = self.client.get('/api/v1/playbooks/')
        internal = PlaybookApi().get()
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    def test_get_http_with_id_parameter(self):
        ctx = ansible_run()
        # Run twice to get a second playbook
        ansible_run()
        playbooks = models.Playbook.query.all()
        self.assertEqual(len(playbooks), 2)

        res = self.client.get('/api/v1/playbooks/', query_string=dict(id=1))
        self.assertEqual(res.status_code, 200)

        data = jsonutils.loads(res.data)
        self.assertEqual(ctx['playbook'].id,
                         data['id'])
        self.assertEqual(ctx['playbook'].path,
                         data['path'])
        self.assertEqual(ctx['playbook'].completed,
                         data['completed'])
        self.assertEqual(ctx['playbook'].started.isoformat(),
                         data['started'])
        self.assertEqual(ctx['playbook'].ended.isoformat(),
                         data['ended'])
        self.assertEqual(ctx['playbook'].parameters,
                         data['parameters'])
        self.assertEqual(ctx['playbook'].ansible_version,
                         data['ansible_version'])
        self.assertEqual(len(ctx['playbook'].files.all()),
                         len(data['files']))
        self.assertEqual(len(ctx['playbook'].hosts.all()),
                         len(data['hosts']))
        self.assertEqual(len(ctx['playbook'].plays.all()),
                         len(data['plays']))
        self.assertEqual(len(ctx['playbook'].results.all()),
                         len(data['results']))
        self.assertEqual(len(ctx['playbook'].tasks.all()),
                         len(data['tasks']))

    def test_get_internal_with_id_parameter(self):
        ansible_run()
        # Run twice to get a second playbook
        ansible_run()
        playbooks = models.Playbook.query.all()
        self.assertEqual(len(playbooks), 2)

        http = self.client.get('/api/v1/playbooks/', query_string=dict(id=1))
        internal = PlaybookApi().get(id=1)
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    def test_get_http_with_id_url(self):
        ctx = ansible_run()
        # Run twice to get a second playbook
        ansible_run()
        playbooks = models.Playbook.query.all()
        self.assertEqual(len(playbooks), 2)

        res = self.client.get('/api/v1/playbooks/1')
        self.assertEqual(res.status_code, 200)

        data = jsonutils.loads(res.data)
        self.assertEqual(ctx['playbook'].id,
                         data['id'])
        self.assertEqual(ctx['playbook'].path,
                         data['path'])
        self.assertEqual(ctx['playbook'].completed,
                         data['completed'])
        self.assertEqual(ctx['playbook'].started.isoformat(),
                         data['started'])
        self.assertEqual(ctx['playbook'].ended.isoformat(),
                         data['ended'])
        self.assertEqual(ctx['playbook'].parameters,
                         data['parameters'])
        self.assertEqual(ctx['playbook'].ansible_version,
                         data['ansible_version'])
        self.assertEqual(len(ctx['playbook'].files.all()),
                         len(data['files']))
        self.assertEqual(len(ctx['playbook'].hosts.all()),
                         len(data['hosts']))
        self.assertEqual(len(ctx['playbook'].plays.all()),
                         len(data['plays']))
        self.assertEqual(len(ctx['playbook'].records.all()),
                         len(data['records']))
        self.assertEqual(len(ctx['playbook'].results.all()),
                         len(data['results']))
        self.assertEqual(len(ctx['playbook'].tasks.all()),
                         len(data['tasks']))

    def test_get_internal_with_id_url(self):
        ansible_run()
        # Run twice to get a second playbook
        ansible_run()
        playbooks = models.Playbook.query.all()
        self.assertEqual(len(playbooks), 2)

        http = self.client.get('/api/v1/playbooks/1')
        internal = PlaybookApi().get(id=1)
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)
