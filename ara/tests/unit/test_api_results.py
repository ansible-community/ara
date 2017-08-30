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

from ara.tests.unit.fakes import FakeRun
from ara.tests.unit.common import TestAra
from ara.api.results import ResultApi
from ara.api.v1.results import RESULT_FIELDS
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
        ctx = FakeRun()
        data = {
            "playbook_id": ctx.playbook['id'],
            "host_id": ctx.playbook['hosts'][0]['id'],
            "play_id": ctx.play['id'],
            "task_id": ctx.t_ok['id'],
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
        ctx = FakeRun()
        data = {
            "playbook_id": ctx.playbook['id'],
            "host_id": ctx.playbook['hosts'][0]['id'],
            "play_id": ctx.play['id'],
            "task_id": ctx.t_ok['id'],
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
            "result": {"msg": "some result"},
            "started": "1970-08-14T00:52:49.570031"
        }
        res = ResultApi().post(data)
        self.assertEqual(res.status_code, 400)

    def test_post_http_with_nonexistant_task(self):
        data = {
            "task_id": 9001,
            "host_id": 1,
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
        self.assertEqual(res.status_code, 404)

    def test_post_internal_with_nonexistant_task(self):
        data = {
            "task_id": 9001,
            "host_id": 1,
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
        self.assertEqual(res.status_code, 404)

    def test_post_http_with_nonexistant_host(self):
        data = {
            "task_id": 1,
            "host_id": 9001,
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
        self.assertEqual(res.status_code, 404)

    def test_post_internal_with_nonexistant_host(self):
        data = {
            "task_id": 1,
            "host_id": 9001,
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
        self.assertEqual(res.status_code, 404)

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
        ctx = FakeRun()
        self.assertEqual(ctx.playbook['results'][0]['id'], 1)

        # Get existing result
        pbresult = self.client.get('/api/v1/results/',
                                   content_type='application/json',
                                   query_string=dict(
                                       id=ctx.playbook['results'][0]['id'])
                                   )
        pbresult = jsonutils.loads(pbresult.data)

        # We'll update the status field, assert we are actually
        # making a change
        new_status = "failed"
        self.assertNotEqual(pbresult['status'], new_status)

        data = {
            "id": pbresult['id'],
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
                                  query_string=dict(id=pbresult['id']))
        updated_result = jsonutils.loads(updated.data)
        self.assertEqual(updated_result['status'], new_status)

    def test_patch_internal_existing(self):
        # Generate fake playbook data
        ctx = FakeRun()
        self.assertEqual(ctx.playbook['results'][0]['id'], 1)

        # Get existing result
        pbresult = ResultApi().get(id=ctx.playbook['results'][0]['id'])
        pbresult = jsonutils.loads(pbresult.data)

        # We'll update the status field, assert we are actually
        # making a change
        new_status = "failed"
        self.assertNotEqual(pbresult['status'], new_status)

        data = {
            "id": pbresult['id'],
            "status": new_status
        }
        res = ResultApi().patch(data)
        self.assertEqual(res.status_code, 200)

        # The patch endpoint should return the full updated object
        data = jsonutils.loads(res.data)
        self.assertEqual(data['status'], new_status)

        # Confirm by re-fetching result
        updated = ResultApi().get(id=pbresult['id'])
        updated_result = jsonutils.loads(updated.data)
        self.assertEqual(updated_result['status'], new_status)

    def test_patch_http_with_missing_arg(self):
        data = {
            "status": "failed"
        }
        res = self.client.patch('/api/v1/results/',
                                data=jsonutils.dumps(data),
                                content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_patch_internal_with_missing_arg(self):
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
        ctx = FakeRun()
        res = self.client.get('/api/v1/results/',
                              content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(ctx.playbook['results']),
                         len(jsonutils.loads(res.data)))

        # TODO: Is ordering weird here ?
        # playbook['results'] doesn't seem to be sorted in the same way as data
        data = jsonutils.loads(res.data)[0]
        self.assertEqual(ctx.playbook['results'][7]['id'], data['id'])

    def test_get_internal_without_parameters(self):
        FakeRun()
        http = self.client.get('/api/v1/results/',
                               content_type='application/json')
        internal = ResultApi().get()
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    def test_get_http_with_id_parameter(self):
        ctx = FakeRun()
        res = self.client.get('/api/v1/results/',
                              content_type='application/json',
                              query_string=dict(id=2))
        self.assertEqual(res.status_code, 200)

        data = jsonutils.loads(res.data)
        self.assertEqual(ctx.playbook['results'][1]['id'], data['id'])

    def test_get_internal_with_id_parameter(self):
        FakeRun()
        http = self.client.get('/api/v1/results/',
                               content_type='application/json',
                               query_string=dict(id=2))
        internal = ResultApi().get(id=2)
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    def test_get_http_with_id_url(self):
        ctx = FakeRun()

        res = self.client.get('/api/v1/results/2',
                              content_type='application/json')
        self.assertEqual(res.status_code, 200)

        data = jsonutils.loads(res.data)
        self.assertEqual(ctx.playbook['results'][1]['id'], data['id'])

    def test_get_internal_with_id_url(self):
        FakeRun()
        http = self.client.get('/api/v1/results/2',
                               content_type='application/json')
        internal = ResultApi().get(id=2)
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)
