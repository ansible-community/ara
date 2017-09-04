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
from ara.api.hosts import HostApi
from ara.api.v1.hosts import HOST_FIELDS


class TestPythonApiHosts(TestAra):
    """ Tests for the ARA API interface """
    def setUp(self):
        super(TestPythonApiHosts, self).setUp()
        self.client = HostApi()

    def tearDown(self):
        super(TestPythonApiHosts, self).tearDown()

    ###########
    # POST
    ###########
    def test_post_with_no_data(self):
        resp, data = self.client.post()
        self.assertEqual(resp.status_code, 400)

    def test_post_with_correct_data(self):
        # Create fake playbook data and create a host in it
        ctx = FakeRun()
        resp, data = self.client.post(
            playbook_id=ctx.playbook['id'],
            name='hostname',
            facts={'ansible_foo': 'bar'},
            changed=1,
            failed=0,
            ok=4,
            skipped=1,
            unreachable=0
        )
        self.assertEqual(resp.status_code, 200)

        # Confirm that the POST returned the full host object ("data")
        # and that the host was really created properly by fetching it
        # ("host")
        resp, host = self.client.get(id=data['id'])
        self.assertEqual(len(data), len(host))
        self.assertEqual(data, host)
        for key in HOST_FIELDS.keys():
            self.assertIn(key, data)
            self.assertIn(key, host)

    def test_post_with_incorrect_data(self):
        resp, data = self.client.post(
            playbook_id='1',
            name=1,
            facts=False,
        )
        self.assertEqual(resp.status_code, 400)

    def test_post_with_missing_argument(self):
        FakeRun()
        resp, data = self.client.post(name='hostname')
        self.assertEqual(resp.status_code, 400)

    def test_post_with_nonexistant_playbook(self):
        resp, data = self.client.post(
            playbook_id=9001,
            name='hostname'
        )
        self.assertEqual(resp.status_code, 404)

    def test_post_host_already_exists(self):
        # Posting the same host a second time should yield a 200 and not error
        # out, hosts are unique per playbook
        ctx = FakeRun()

        # Retrieve a host so we can post the same thing
        resp, pbhost = self.client.get(playbook_id=ctx.playbook['id'])
        pbhost = pbhost[0]

        resp, data = self.client.post(
            playbook_id=pbhost['playbook']['id'],
            name=pbhost['name'],
            facts=pbhost['facts'],
            changed=pbhost['changed'],
            failed=pbhost['failed'],
            ok=pbhost['ok'],
            skipped=pbhost['skipped'],
            unreachable=pbhost['unreachable']
        )
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(pbhost['id'], data['id'])

    ###########
    # PATCH
    ###########
    def test_patch_with_no_data(self):
        resp, data = self.client.patch()
        self.assertEqual(resp.status_code, 400)

    def test_patch_existing(self):
        # Generate fake playbook data
        ctx = FakeRun()
        self.assertEqual(ctx.playbook['hosts'][0]['id'], 1)

        # Get existing host
        resp, pbhost = self.client.get(id=ctx.playbook['hosts'][0]['id'])

        # We'll update the name field, assert we are actually
        # making a change
        new_name = "Updated_hostname"
        self.assertNotEqual(pbhost['name'], new_name)

        resp, data = self.client.patch(
            id=pbhost['id'],
            name=new_name
        )
        self.assertEqual(resp.status_code, 200)

        # The patch endpoint should return the full updated object
        self.assertEqual(data['name'], new_name)

        # Confirm by re-fetching host
        resp, updated = self.client.get(id=pbhost['id'])
        self.assertEqual(updated['name'], new_name)

    def test_patch_with_missing_arg(self):
        FakeRun()
        resp, data = self.client.patch(
            name='Updated_hostname'
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
        self.assertEqual(len(ctx.playbook['hosts']),
                         len(data))

        # TODO: Is ordering weird here ?
        # playbook['hosts'] doesn't seem to be sorted in the same way as data
        self.assertEqual(ctx.playbook['hosts'][1]['id'], data[0]['id'])

    def test_get_with_id_parameter(self):
        ctx = FakeRun()
        resp, data = self.client.get(id=2)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(ctx.playbook['hosts'][1]['id'], data['id'])
