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
from ara.api.plays import PlayApi
from ara.api.v1.plays import PLAY_FIELDS


class TestApiPlays(TestAra):
    """ Tests for the ARA API interface """
    def setUp(self):
        super(TestApiPlays, self).setUp()
        self.client = PlayApi()

    def tearDown(self):
        super(TestApiPlays, self).tearDown()

    ###########
    # POST
    ###########
    def test_post_with_no_data(self):
        resp, data = self.client.post()
        self.assertEqual(resp.status_code, 400)

    def test_post_with_correct_data(self):
        # Create fake playbook data and create a play in it
        ctx = FakeRun()
        resp, data = self.client.post(
            playbook_id=ctx.playbook['id'],
            name='Play from unit tests',
            started='1970-08-14T00:52:49.570031'
        )
        self.assertEqual(resp.status_code, 200)

        # Confirm that the POST returned the full play object ("data")
        # and that the play was really created properly by fetching it
        # ("play")
        resp, play = self.client.get(id=data['id'])
        self.assertEqual(len(data), len(play))
        self.assertEqual(data, play)
        for key in PLAY_FIELDS.keys():
            self.assertIn(key, data)
            self.assertIn(key, play)

    def test_post_with_incorrect_data(self):
        FakeRun()
        resp, data = self.client.post(
            playbook_id='1',
            name=1,
            started='a long time ago'
        )
        self.assertEqual(resp.status_code, 400)

    def test_post_with_missing_argument(self):
        FakeRun()
        resp, data = self.client.post(
            name='Play from unit tests',
            started='1970-08-14T00:52:49.570031'
        )
        self.assertEqual(resp.status_code, 400)

    def test_post_with_nonexistant_playbook(self):
        resp, data = self.client.post(
            playbook_id=9001,
            name='Play from unit tests',
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
        self.assertEqual(ctx.play['id'], 1)

        # We'll update the name field, assert we are actually
        # making a change
        new_name = "Updated play name"
        self.assertNotEqual(ctx.play['name'], new_name)

        resp, data = self.client.patch(
            id=ctx.play['id'],
            name=new_name
        )
        self.assertEqual(resp.status_code, 200)

        # The patch endpoint should return the full updated object
        self.assertEqual(data['name'], new_name)

        # Confirm by re-fetching play
        resp, updated = self.client.get(id=ctx.play['id'])
        self.assertEqual(updated['name'], new_name)

    def test_patch_with_missing_arg(self):
        FakeRun()
        resp, data = self.client.patch(
            name='Updated play name'
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

        self.assertEqual(len(data), len(ctx.play))
        self.assertEqual(data, ctx.play)
        for key in PLAY_FIELDS.keys():
            self.assertIn(key, data)
            self.assertIn(key, ctx.play)

    def test_get_with_id_parameter(self):
        FakeRun()
        # Run twice to get a second play
        ctx = FakeRun()
        resp, plays = self.client.get()
        self.assertEqual(len(plays), 2)

        resp, data = self.client.get(id=2)
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(len(data), len(ctx.play))
        self.assertEqual(data, ctx.play)
        for key in PLAY_FIELDS.keys():
            self.assertIn(key, data)
            self.assertIn(key, ctx.play)
