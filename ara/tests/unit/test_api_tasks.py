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
from ara.api.tasks import TaskApi
from ara.api.v1.tasks import TASK_FIELDS


class TestPythonApiTasks(TestAra):
    """ Tests for the ARA API interface """
    def setUp(self):
        super(TestPythonApiTasks, self).setUp()
        self.client = TaskApi()

    def tearDown(self):
        super(TestPythonApiTasks, self).tearDown()

    ###########
    # POST
    ###########
    def test_post_with_no_data(self):
        resp, data = self.client.post()
        self.assertEqual(resp.status_code, 400)

    def test_post_with_correct_data(self):
        # Create fake playbook data and create a task in a play
        ctx = FakeRun()
        resp, data = self.client.post(
            play_id=ctx.play['id'],
            file_id=ctx.playbook['files'][0]['id'],
            name='Task from unit tests',
            action='debug',
            lineno=1,
            tags=['one', 'two'],
            started='1970-08-14T00:52:49.570031'
        )
        self.assertEqual(resp.status_code, 200)

        # Confirm that the POST returned the full task object ("data")
        # and that the task was really created properly by fetching it
        # ("task")
        resp, task = self.client.get(id=data['id'])
        self.assertEqual(len(data), len(task))
        self.assertEqual(data, task)
        for key in TASK_FIELDS.keys():
            self.assertIn(key, data)
            self.assertIn(key, task)

    def test_post_with_incorrect_data(self):
        FakeRun()
        resp, data = self.client.post(
            play_id='one',
            file_id='False',
            name=1,
            action=None,
            lineno='two',
            tags='None',
            started=False
        )
        self.assertEqual(resp.status_code, 400)

    def test_post_with_missing_argument(self):
        FakeRun()
        resp, data = self.client.post(
            name='Task from unit tests',
            action='debug',
            lineno=1,
            tags=['one', 'two'],
            started='1970-08-14T00:52:49.570031'
        )
        self.assertEqual(resp.status_code, 400)

    def test_post_with_nonexistant_play(self):
        FakeRun()
        resp, data = self.client.post(
            play_id=9001,
            file_id=1,
            name='Task from unit tests',
            action='debug',
            lineno=1,
            tags=['one', 'two'],
            started='1970-08-14T00:52:49.570031'
        )
        self.assertEqual(resp.status_code, 404)

    def test_post_with_nonexistant_file(self):
        FakeRun()
        resp, data = self.client.post(
            play_id=1,
            file_id=9001,
            name='Task from unit tests',
            action='debug',
            lineno=1,
            tags=['one', 'two'],
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
        self.assertEqual(ctx.t_ok['id'], 1)

        # Get existing task
        resp, pbtask = self.client.get(id=ctx.t_ok['id'])

        # We'll update the name field, assert we are actually
        # making a change
        new_name = "Updated task name"
        self.assertNotEqual(pbtask['name'], new_name)

        resp, data = self.client.patch(
            id=pbtask['id'],
            name=new_name
        )
        self.assertEqual(resp.status_code, 200)

        # The patch endpoint should return the full updated object
        self.assertEqual(data['name'], new_name)

        # Confirm by re-fetching task
        resp, updated = self.client.get(id=pbtask['id'])
        self.assertEqual(updated['name'], new_name)

    def test_patch_with_missing_arg(self):
        resp, data = self.client.patch(
            name='Updated task name'
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

        data = data[4]

        self.assertEqual(len(data), len(ctx.t_ok))
        self.assertEqual(data, ctx.t_ok)
        for key in TASK_FIELDS.keys():
            self.assertIn(key, data)
            self.assertIn(key, ctx.t_ok)

    def test_get_with_id_parameter(self):
        ctx = FakeRun()

        resp, data = self.client.get(id=1)
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(len(data), len(ctx.t_ok))
        self.assertEqual(data, ctx.t_ok)
        for key in TASK_FIELDS.keys():
            self.assertIn(key, data)
            self.assertIn(key, ctx.t_ok)
