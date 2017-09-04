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
from ara.api.records import RecordApi
from ara.api.v1.records import RECORD_FIELDS


class TestPythonApiRecords(TestAra):
    """ Tests for the ARA API interface """
    def setUp(self):
        super(TestPythonApiRecords, self).setUp()
        self.client = RecordApi()

    def tearDown(self):
        super(TestPythonApiRecords, self).tearDown()

    ###########
    # POST
    ###########
    def test_post_with_no_data(self):
        resp, data = self.client.post()
        self.assertEqual(resp.status_code, 400)

    def test_post_with_correct_data(self):
        # Create fake playbook data and create a record in it
        ctx = FakeRun()
        resp, data = self.client.post(
            playbook_id=ctx.playbook['id'],
            key='foo',
            value='bar',
            type='text'
        )
        self.assertEqual(resp.status_code, 200)

        # Confirm that the POST returned the full record object ("data")
        # and that the record was really created properly by fetching it
        # ("record")
        resp, record = self.client.get(id=data['id'])
        self.assertEqual(len(data), len(record))
        self.assertEqual(data, record)
        for key in RECORD_FIELDS.keys():
            self.assertIn(key, data)
            self.assertIn(key, record)

    def test_post_with_incorrect_data(self):
        FakeRun()
        resp, data = self.client.post(
            playbook_id='1',
            key=1,
            value=False,
            type='binary'
        )
        self.assertEqual(resp.status_code, 400)

    def test_post_with_missing_argument(self):
        FakeRun()
        resp, data = self.client.post(
            key='foo',
            value='bar',
            type='text'
        )
        self.assertEqual(resp.status_code, 400)

    def test_post_with_nonexistant_playbook(self):
        resp, data = self.client.post(
            playbook_id=9001,
            key='foo',
            value='bar',
            type='text'
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
        self.assertEqual(ctx.playbook['records'][0]['id'], 1)

        # Get existing record
        resp, pbrecord = self.client.get(id=ctx.playbook['records'][0]['id'])

        # We'll update the value field, assert we are actually
        # making a change
        new_value = "Updated value"
        self.assertNotEqual(pbrecord['value'], new_value)

        resp, data = self.client.patch(
            id=pbrecord['id'],
            value=new_value
        )
        self.assertEqual(resp.status_code, 200)

        # The patch endpoint should return the full updated object
        self.assertEqual(data['value'], new_value)

        # Confirm by re-fetching record
        resp, updated = self.client.get(id=pbrecord['id'])
        self.assertEqual(updated['value'], new_value)

    def test_patch_with_missing_arg(self):
        FakeRun()
        resp, data = self.client.patch(
            value='Updated value'
        )
        self.assertEqual(resp.status_code, 400)

    ###########
    # PUT
    ###########
    # Not implemented yet
    def test_put_unimplemented(self):
        resp, data = self.client.put()
        self.assertEqual(resp.status_code, 405)

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
        FakeRun()
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

        data = data[0]
        self.assertEqual(ctx.playbook['records'][0]['id'], data['id'])

    def test_get_with_id_parameter(self):
        FakeRun()
        # Run twice to get a second record
        ctx = FakeRun()
        resp, records = self.client.get()
        self.assertEqual(len(records), 2)

        resp, data = self.client.get(id=2)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(ctx.playbook['records'][0]['id'], data['id'])
