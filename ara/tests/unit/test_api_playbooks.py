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
from ara.api.playbooks import PlaybookApi
from ara.api.v1.playbooks import PLAYBOOK_FIELDS


class TestPythonApiPlaybooks(TestAra):
    """ Tests for the ARA API interface """
    def setUp(self):
        super(TestPythonApiPlaybooks, self).setUp()
        self.client = PlaybookApi()

    def tearDown(self):
        super(TestPythonApiPlaybooks, self).tearDown()

    ###########
    # POST
    ###########
    def test_post_with_no_data(self):
        resp, data = self.client.post()
        self.assertEqual(resp.status_code, 400)

    def test_post_with_correct_data(self):
        # Create a new playbook
        resp, data = self.client.post(
            path='/root/playbook.yml',
            ansible_version='2.2.3.1',
            parameters={
                'become': True,
                'become_user': 'root'
            },
            completed=False,
            started='1970-08-14T00:52:49.570031'
        )
        self.assertEqual(resp.status_code, 200)

        # Confirm that the POST returned the full playbook object ("data")
        # and that the playbook was really created properly by fetching it
        # ("playbook")
        resp, playbook = self.client.get(id=data['id'])
        self.assertEqual(len(data), len(playbook))
        self.assertEqual(data, playbook)
        for key in PLAYBOOK_FIELDS.keys():
            self.assertIn(key, data)
            self.assertIn(key, playbook)

    def test_post_with_incorrect_data(self):
        resp, data = self.client.post(
            path=False,
            ansible_version=2,
            parameters=['one'],
            completed='yes',
            started='a long time ago'
        )
        self.assertEqual(resp.status_code, 400)

    def test_post_with_missing_argument(self):
        resp, data = self.client.post(
            path='/root/playbook.yml'
        )
        self.assertEqual(resp.status_code, 400)

    ###########
    # PATCH
    ###########
    def test_patch_with_no_data(self):
        resp, data = self.client.patch()
        self.assertEqual(resp.status_code, 400)

    def test_patch_existing(self):
        # Generate fake playbook data
        ctx = FakeRun()
        self.assertEqual(ctx.playbook['id'], 1)

        # We'll update the ansible_version field, assert we are actually
        # making a change
        new_version = "1.9.9.6"
        self.assertNotEqual(ctx.playbook['ansible_version'], new_version)

        resp, data = self.client.patch(
            id=ctx.playbook['id'],
            ansible_version=new_version
        )
        self.assertEqual(resp.status_code, 200)

        # The patch endpoint should return the full updated object
        self.assertEqual(data['ansible_version'], new_version)

        # Confirm by re-fetching playbook
        resp, updated = self.client.get(id=ctx.playbook['id'])
        self.assertEqual(updated['ansible_version'], new_version)

    def test_patch_with_missing_arg(self):
        FakeRun()
        resp, data = self.client.patch(
            ansible_version='1.9.9.6'
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

        self.assertEqual(len(data), len(ctx.playbook))
        self.assertEqual(data, ctx.playbook)
        for key in PLAYBOOK_FIELDS.keys():
            self.assertIn(key, data)
            self.assertIn(key, ctx.playbook)

    def test_get_with_id_parameter(self):
        FakeRun()
        # Run twice to get a second playbook
        ctx = FakeRun()
        resp, playbooks = self.client.get()
        self.assertEqual(len(playbooks), 2)

        resp, data = self.client.get(id=2)
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(len(data), len(ctx.playbook))
        self.assertEqual(data, ctx.playbook)
        for key in PLAYBOOK_FIELDS.keys():
            self.assertIn(key, data)
            self.assertIn(key, ctx.playbook)
