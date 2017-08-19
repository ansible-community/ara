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
from ara.api.results import ResultApi
from ara.api.v1.results import RESULT_FIELDS
import ara.db.models as models
import pytest

from oslo_serialization import jsonutils
from werkzeug.routing import RequestRedirect


class TestApiResults(TestAra):
    """ Tests for the ARA API interface """
    def setUp(self):
        super(TestApiResults, self).setUp()

    def tearDown(self):
        super(TestApiResults, self).tearDown()

    ###########
    # POST
    ###########
    def test_post_http_redirect(self):
        res = self.client.post('/api/v1/results')
        self.assertEqual(res.status_code, 301)

    def test_post_http_with_no_data(self):
        res = self.client.post('/api/v1/results/',
                               content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_post_internal_with_no_data(self):
        res = ResultApi().post()
        self.assertEqual(res.status_code, 400)

    def test_post_http_with_correct_data(self):
        # Create fake playbook data and create a result in it
        ctx = ansible_run()
        data = {
            "playbook_id": ctx['playbook'].id,
            "host_id": ctx['host'].id,
            "play_id": ctx['play'].id,
            "task_id": ctx['task'].id,
            "status": "ok",
            "changed": True,
            "failed": False,
            "skipped": False,
            "unreachable": False,
            "ignore_errors": False,
            "result": {"msg": "some result"},
            "started": "1970-08-14T00:52:49.570031"
        }

        res = self.client.post('/api/v1/results/',
                               data=jsonutils.dumps(data),
                               content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = jsonutils.loads(res.data)

        # Confirm that the POST returned the full result object ("data")
        # and that the result was really created properly by fetching it
        # ("result")
        result = self.client.get('/api/v1/results/',
                                 content_type='application/json',
                                 query_string=dict(id=data['id']))
        result = jsonutils.loads(result.data)
        self.assertEqual(len(data), len(result))
        self.assertEqual(data, result)
        for key in RESULT_FIELDS.keys():
            self.assertIn(key, data)
            self.assertIn(key, result)

    def test_post_internal_with_correct_data(self):
        # Create fake playbook data and create a result in it
        ctx = ansible_run()
        data = {
            "playbook_id": ctx['playbook'].id,
            "host_id": ctx['host'].id,
            "play_id": ctx['play'].id,
            "task_id": ctx['task'].id,
            "status": "ok",
            "changed": True,
            "failed": False,
            "skipped": False,
            "unreachable": False,
            "ignore_errors": False,
            "result": {"msg": "some result"},
            "started": "1970-08-14T00:52:49.570031"
        }

        res = ResultApi().post(data)
        self.assertEqual(res.status_code, 200)
        data = jsonutils.loads(res.data)

        # Confirm that the POST returned the full result object ("data")
        # and that the result was really created properly by fetching it
        # ("result")
        result = ResultApi().get(id=data['id'])
        result = jsonutils.loads(result.data)
        self.assertEqual(len(data), len(result))
        self.assertEqual(data, result)
        for key in RESULT_FIELDS.keys():
            self.assertIn(key, data)
            self.assertIn(key, result)

    def test_post_http_with_incorrect_data(self):
        data = {
            "playbook_id": "one",
            "host_id": "two",
            "play_id": "three",
            "task_id": "four",
            "status": True,
            "changed": "yes",
            "failed": "no",
            "skipped": "no",
            "unreachable": "no",
            "ignore_errors": "no",
            "result": '{"msg": "some result"}',
            "started": "a long time ago"
        }

        res = self.client.post('/api/v1/results/',
                               data=jsonutils.dumps(data),
                               content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_post_internal_with_incorrect_data(self):
        data = {
            "playbook_id": "one",
            "host_id": "two",
            "play_id": "three",
            "task_id": "four",
            "status": True,
            "changed": "yes",
            "failed": "no",
            "skipped": "no",
            "unreachable": "no",
            "ignore_errors": "no",
            "result": {"msg": "some result"},
            "started": "a long time ago"
        }

        res = ResultApi().post(data)
        self.assertEqual(res.status_code, 400)

    def test_post_http_with_missing_argument(self):
        data = {
            "status": "ok",
            "changed": True,
            "failed": False,
            "skipped": False,
            "unreachable": False,
            "ignore_errors": False,
            "result": '{"msg": "some result"}',
            "started": "1970-08-14T00:52:49.570031"
        }
        res = self.client.post('/api/v1/results/',
                               data=jsonutils.dumps(data),
                               content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_post_internal_with_missing_argument(self):
        data = {
            "status": "ok",
            "changed": True,
            "failed": False,
            "skipped": False,
            "unreachable": False,
            "ignore_errors": False,
            "result": '{"msg": "some result"}',
            "started": "1970-08-14T00:52:49.570031"
        }
        res = ResultApi().post(data)
        self.assertEqual(res.status_code, 400)

    ###########
    # PATCH
    ###########
    def test_patch_http_redirect(self):
        res = self.client.patch('/api/v1/results')
        self.assertEqual(res.status_code, 301)

    def test_patch_http_with_no_data(self):
        res = self.client.patch('/api/v1/results/',
                                content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_patch_internal_with_no_data(self):
        res = ResultApi().patch()
        self.assertEqual(res.status_code, 400)

    def test_patch_http_existing(self):
        # Generate fake playbook data
        ctx = ansible_run()
        self.assertEqual(ctx['result'].id, 1)

        # We'll update the status field, assert we are actually
        # making a change
        new_status = "failed"
        self.assertNotEqual(ctx['result'].status, new_status)

        data = {
            "id": ctx['result'].id,
            "status": new_status
        }
        res = self.client.patch('/api/v1/results/',
                                data=jsonutils.dumps(data),
                                content_type='application/json')
        self.assertEqual(res.status_code, 200)

        # The patch endpoint should return the full updated object
        data = jsonutils.loads(res.data)
        self.assertEqual(data['status'], new_status)

        # Confirm by re-fetching result
        updated = self.client.get('/api/v1/results/',
                                  content_type='application/json',
                                  query_string=dict(id=ctx['result'].id))
        updated_result = jsonutils.loads(updated.data)
        self.assertEqual(updated_result['status'], new_status)

    def test_patch_internal_existing(self):
        # Generate fake playbook data
        ctx = ansible_run()
        self.assertEqual(ctx['result'].id, 1)

        # We'll update the status field, assert we are actually
        # making a change
        new_status = "failed"
        self.assertNotEqual(ctx['result'].status, new_status)

        data = {
            "id": ctx['result'].id,
            "status": new_status
        }
        res = ResultApi().patch(data)
        self.assertEqual(res.status_code, 200)

        # The patch endpoint should return the full updated object
        data = jsonutils.loads(res.data)
        self.assertEqual(data['status'], new_status)

        # Confirm by re-fetching result
        updated = ResultApi().get(id=ctx['result'].id)
        updated_result = jsonutils.loads(updated.data)
        self.assertEqual(updated_result['status'], new_status)

    def test_patch_http_with_missing_arg(self):
        ansible_run()
        data = {
            "status": "failed"
        }
        res = self.client.patch('/api/v1/results/',
                                data=jsonutils.dumps(data),
                                content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_patch_internal_with_missing_arg(self):
        ansible_run()
        data = {
            "status": "failed"
        }
        res = ResultApi().patch(data)
        self.assertEqual(res.status_code, 400)

    ###########
    # DELETE
    ###########
    def test_delete_http_redirect(self):
        # TODO: Does this raise a RequestRedirect due to underlying 405 ?
        with pytest.raises(RequestRedirect):
            self.client.delete('/api/v1/results')

    # Not implemented yet
    def test_delete_http_unimplemented(self):
        res = self.client.delete('/api/v1/results/')
        self.assertEqual(res.status_code, 405)

    def test_delete_internal_unimplemented(self):
        http = self.client.delete('/api/v1/results/')
        internal = ResultApi().delete()
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    ###########
    # GET
    ###########
    def test_get_http_redirect(self):
        res = self.client.get('/api/v1/results',
                              content_type='application/json')
        self.assertEqual(res.status_code, 301)

    def test_get_http_with_bad_params_404_help(self):
        res = self.client.get('/api/v1/results/',
                              content_type='application/json',
                              query_string=dict(id=0))
        self.assertEqual(res.status_code, 404)
        # TODO: Improve this
        self.assertTrue(b'result_output' in res.data)
        self.assertTrue(b'query_parameters' in res.data)

    def test_get_internal_with_bad_params_404_help(self):
        http = self.client.get('/api/v1/results/',
                               content_type='application/json',
                               query_string=dict(id=0))
        internal = ResultApi().get(id=0)
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    def test_get_http_without_parameters_and_data(self):
        res = self.client.get('/api/v1/results/',
                              content_type='application/json')
        self.assertEqual(res.status_code, 404)
        # TODO: Improve this
        self.assertTrue(b'result_output' in res.data)
        self.assertTrue(b'query_parameters' in res.data)

    def test_get_internal_without_parameters_and_data(self):
        http = self.client.get('/api/v1/results/',
                               content_type='application/json')
        internal = ResultApi().get()
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    def test_get_http_without_parameters(self):
        ctx = ansible_run()
        res = self.client.get('/api/v1/results/',
                              content_type='application/json')
        self.assertEqual(res.status_code, 200)

        data = jsonutils.loads(res.data)[2]

        self.assertEqual(ctx['result'].id,
                         data['id'])
        self.assertEqual(ctx['result'].playbook_id,
                         data['playbook_id'])
        self.assertEqual(ctx['result'].play_id,
                         data['play_id'])
        self.assertEqual(ctx['result'].task_id,
                         data['task_id'])
        self.assertEqual(ctx['result'].host_id,
                         data['host_id'])
        self.assertEqual(ctx['result'].status,
                         data['status'])
        self.assertEqual(ctx['result'].changed,
                         data['changed'])
        self.assertEqual(ctx['result'].failed,
                         data['failed'])
        self.assertEqual(ctx['result'].skipped,
                         data['skipped'])
        self.assertEqual(ctx['result'].unreachable,
                         data['unreachable'])
        self.assertEqual(ctx['result'].ignore_errors,
                         data['ignore_errors'])
        self.assertEqual(ctx['result'].result,
                         data['result'])
        self.assertEqual(ctx['result'].started.isoformat(),
                         data['started'])
        self.assertEqual(ctx['result'].ended.isoformat(),
                         data['ended'])

    def test_get_internal_without_parameters(self):
        ansible_run()
        http = self.client.get('/api/v1/results/',
                               content_type='application/json')
        internal = ResultApi().get()
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    def test_get_http_with_id_parameter(self):
        ctx = ansible_run()
        # Run twice to get a second playbook
        ansible_run()
        playbooks = models.Playbook.query.all()
        self.assertEqual(len(playbooks), 2)

        res = self.client.get('/api/v1/results/',
                              content_type='application/json',
                              query_string=dict(id=1))
        self.assertEqual(res.status_code, 200)

        data = jsonutils.loads(res.data)
        self.assertEqual(ctx['result'].id,
                         data['id'])
        self.assertEqual(ctx['result'].playbook_id,
                         data['playbook_id'])
        self.assertEqual(ctx['result'].play_id,
                         data['play_id'])
        self.assertEqual(ctx['result'].task_id,
                         data['task_id'])
        self.assertEqual(ctx['result'].host_id,
                         data['host_id'])
        self.assertEqual(ctx['result'].status,
                         data['status'])
        self.assertEqual(ctx['result'].changed,
                         data['changed'])
        self.assertEqual(ctx['result'].failed,
                         data['failed'])
        self.assertEqual(ctx['result'].skipped,
                         data['skipped'])
        self.assertEqual(ctx['result'].unreachable,
                         data['unreachable'])
        self.assertEqual(ctx['result'].ignore_errors,
                         data['ignore_errors'])
        self.assertEqual(ctx['result'].result,
                         data['result'])
        self.assertEqual(ctx['result'].started.isoformat(),
                         data['started'])
        self.assertEqual(ctx['result'].ended.isoformat(),
                         data['ended'])

    def test_get_internal_with_id_parameter(self):
        ansible_run()
        # Run twice to get a second playbook
        ansible_run()
        playbooks = models.Playbook.query.all()
        self.assertEqual(len(playbooks), 2)

        http = self.client.get('/api/v1/results/',
                               content_type='application/json',
                               query_string=dict(id=1))
        internal = ResultApi().get(id=1)
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    def test_get_http_with_id_url(self):
        ctx = ansible_run()
        # Run twice to get a second playbook
        ansible_run()
        playbooks = models.Playbook.query.all()
        self.assertEqual(len(playbooks), 2)

        res = self.client.get('/api/v1/results/1',
                              content_type='application/json')
        self.assertEqual(res.status_code, 200)

        data = jsonutils.loads(res.data)
        self.assertEqual(ctx['result'].id,
                         data['id'])
        self.assertEqual(ctx['result'].playbook_id,
                         data['playbook_id'])
        self.assertEqual(ctx['result'].play_id,
                         data['play_id'])
        self.assertEqual(ctx['result'].task_id,
                         data['task_id'])
        self.assertEqual(ctx['result'].host_id,
                         data['host_id'])
        self.assertEqual(ctx['result'].status,
                         data['status'])
        self.assertEqual(ctx['result'].changed,
                         data['changed'])
        self.assertEqual(ctx['result'].failed,
                         data['failed'])
        self.assertEqual(ctx['result'].skipped,
                         data['skipped'])
        self.assertEqual(ctx['result'].unreachable,
                         data['unreachable'])
        self.assertEqual(ctx['result'].ignore_errors,
                         data['ignore_errors'])
        self.assertEqual(ctx['result'].result,
                         data['result'])
        self.assertEqual(ctx['result'].started.isoformat(),
                         data['started'])
        self.assertEqual(ctx['result'].ended.isoformat(),
                         data['ended'])

    def test_get_internal_with_id_url(self):
        ansible_run()
        # Run twice to get a second playbook
        ansible_run()
        playbooks = models.Playbook.query.all()
        self.assertEqual(len(playbooks), 2)

        http = self.client.get('/api/v1/results/1',
                               content_type='application/json')
        internal = ResultApi().get(id=1)
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)
