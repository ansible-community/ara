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


class TestPythonApiResults(TestAra):
    """ Tests for the ARA API interface """
    def setUp(self):
        super(TestPythonApiResults, self).setUp()
        self.client = ResultApi()

    def tearDown(self):
        super(TestPythonApiResults, self).tearDown()

    ###########
    # POST
    ###########
    def test_post_with_no_data(self):
        resp, data = self.client.post()
        self.assertEqual(resp.status_code, 400)

    def test_post_with_correct_data(self):
        # Create fake playbook data and create a result in it
        ctx = FakeRun()
        resp, data = self.client.post(
            host_id=ctx.playbook['hosts'][0]['id'],
            task_id=ctx.t_ok['id'],
            status='ok',
            changed=True,
            failed=False,
            skipped=False,
            unreachable=False,
            ignore_errors=False,
            result={'msg': 'some result'},
            started='1970-08-14T00:52:49.570031'
        )
        self.assertEqual(resp.status_code, 200)

        # Confirm that the POST returned the full result object ("data")
        # and that the result was really created properly by fetching it
        # ("result")
        resp, result = self.client.get(id=data['id'])
        self.assertEqual(len(data), len(result))
        self.assertEqual(data, result)
        for key in RESULT_FIELDS.keys():
            self.assertIn(key, data)
            self.assertIn(key, result)

    def test_post_with_incorrect_data(self):
        resp, data = self.client.post(
            host_id='two',
            task_id='four',
            status=True,
            changed='yes',
            failed='no',
            skipped='no',
            unreachable='no',
            ignore_errors='no',
            result="{'msg': 'some result'}",
            started='a long time ago'
        )
        self.assertEqual(resp.status_code, 400)

    def test_post_with_missing_argument(self):
        resp, data = self.client.post(
            status='ok',
            changed=True,
            failed=False,
            skipped=False,
            unreachable=False,
            ignore_errors=False,
            result={'msg': 'some result'},
            started='1970-08-14T00:52:49.570031'
        )
        self.assertEqual(resp.status_code, 400)

    def test_post_with_nonexistant_host(self):
        FakeRun()
        resp, data = self.client.post(
            host_id=9001,
            task_id=1,
            status='ok',
            changed=True,
            failed=False,
            skipped=False,
            unreachable=False,
            ignore_errors=False,
            result={'msg': 'some result'},
            started='1970-08-14T00:52:49.570031'
        )
        self.assertEqual(resp.status_code, 404)

    def test_post_with_nonexistant_task(self):
        resp, data = self.client.post(
            host_id=1,
            task_id=9001,
            status='ok',
            changed=True,
            failed=False,
            skipped=False,
            unreachable=False,
            ignore_errors=False,
            result={'msg': 'some result'},
            started='1970-08-14T00:52:49.570031'
        )
        self.assertEqual(resp.status_code, 404)

    ###########
    # PATCH
    ###########
    def test_patch_with_no_data(self):
        resp, data = self.client.patch()
        self.assertEqual(resp.status_code, 400)

    def test_patch_existing(self):
        # Generate fake playbook data
        ctx = FakeRun()
        self.assertEqual(ctx.playbook['results'][0]['id'], 1)

        # Get existing result
        resp, pbresult = self.client.get(id=ctx.playbook['results'][0]['id'])

        # We'll update the status field, assert we are actually
        # making a change
        new_status = 'failed'
        self.assertNotEqual(pbresult['status'], new_status)

        resp, data = self.client.patch(
            id=pbresult['id'],
            status=new_status
        )
        self.assertEqual(resp.status_code, 200)

        # The patch endpoint should return the full updated object
        self.assertEqual(data['status'], new_status)

        # Confirm by re-fetching result
        resp, updated = self.client.get(id=pbresult['id'])
        self.assertEqual(updated['status'], new_status)

    def test_patch_with_missing_arg(self):
        resp, data = self.client.patch(
            status='failed'
        )
        self.assertEqual(resp.status_code, 400)

    ###########
    # DELETE
    ###########
    # Not implemented yet
    def test_delete_unimplemented(self):
        resp, data = self.client.delete()
        self.assertEqual(resp.status_code, 405)

    ###########
    # GET
    ###########
    def test_get_with_bad_params_404_help(self):
        resp, data = self.client.get(id=0)
        self.assertEqual(resp.status_code, 404)
        # TODO: Improve this
        self.assertTrue('result_output' in data['help'])
        self.assertTrue('query_parameters' in data['help'])

    def test_get_without_parameters_and_data(self):
        resp, data = self.client.get()
        self.assertEqual(resp.status_code, 404)
        # TODO: Improve this
        self.assertTrue('result_output' in data['help'])
        self.assertTrue('query_parameters' in data['help'])

    def test_get_without_parameters(self):
        ctx = FakeRun()
        resp, data = self.client.get()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(ctx.playbook['results']),
                         len(data))

        # TODO: Is ordering weird here ?
        # playbook['results'] doesn't seem to be sorted in the same way as data
        data = data[0]
        self.assertEqual(ctx.playbook['results'][7]['id'], data['id'])

    def test_get_with_id_parameter(self):
        ctx = FakeRun()
        resp, data = self.client.get(id=2)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(ctx.playbook['results'][1]['id'], data['id'])
