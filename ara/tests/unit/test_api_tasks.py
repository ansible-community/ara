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
from ara.api.tasks import TaskApi
from ara.api.v1.tasks import TASK_FIELDS
import ara.db.models as models
import pytest

from oslo_serialization import jsonutils
from werkzeug.routing import RequestRedirect


class TestApiTasks(TestAra):
    """ Tests for the ARA API interface """
    def setUp(self):
        super(TestApiTasks, self).setUp()

    def tearDown(self):
        super(TestApiTasks, self).tearDown()

    ###########
    # POST
    ###########
    def test_post_http_redirect(self):
        res = self.client.post('/api/v1/tasks')
        self.assertEqual(res.status_code, 301)

    def test_post_http_with_no_data(self):
        res = self.client.post('/api/v1/tasks/',
                               content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_post_internal_with_no_data(self):
        res = TaskApi().post()
        self.assertEqual(res.status_code, 400)

    def test_post_http_with_correct_data(self):
        # Create fake playbook data and create a task in a play
        ctx = ansible_run()
        data = {
            "playbook_id": ctx['playbook'].id,
            "play_id": ctx['play'].id,
            "file_id": ctx['playbook'].file.id,
            "name": "Task from unit tests",
            "action": "debug",
            "lineno": 1,
            "tags": ['one', 'two'],
            "started": "1970-08-14T00:52:49.570031"
        }
        res = self.client.post('/api/v1/tasks/',
                               data=jsonutils.dumps(data),
                               content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = jsonutils.loads(res.data)

        # Confirm that the POST returned the full task object ("data")
        # and that the task was really created properly by fetching it
        # ("task")
        task = self.client.get('/api/v1/tasks/',
                               content_type='application/json',
                               query_string=dict(id=data['id']))
        task = jsonutils.loads(task.data)
        self.assertEqual(len(data), len(task))
        self.assertEqual(data, task)
        for key in TASK_FIELDS.keys():
            self.assertIn(key, data)
            self.assertIn(key, task)

    def test_post_internal_with_correct_data(self):
        # Create fake playbook data and create a task in a play
        ctx = ansible_run()
        data = {
            "playbook_id": ctx['playbook'].id,
            "play_id": ctx['play'].id,
            "file_id": ctx['playbook'].file.id,
            "name": "Task from unit tests",
            "action": "debug",
            "lineno": 1,
            "tags": ['one', 'two'],
            "started": "1970-08-14T00:52:49.570031"
        }
        res = TaskApi().post(data)
        self.assertEqual(res.status_code, 200)
        data = jsonutils.loads(res.data)

        # Confirm that the POST returned the full task object ("data")
        # and that the task was really created properly by fetching it
        # ("task")
        task = TaskApi().get(id=data['id'])
        task = jsonutils.loads(task.data)
        self.assertEqual(len(data), len(task))
        self.assertEqual(data, task)
        for key in TASK_FIELDS.keys():
            self.assertIn(key, data)
            self.assertIn(key, task)

    def test_post_http_with_incorrect_data(self):
        data = {
            "playbook_id": "1",
            "play_id": "one",
            "file_id": "False",
            "name": 1,
            "action": None,
            "lineno": "two",
            "tags": "None",
            "started": False
        }

        res = self.client.post('/api/v1/tasks/',
                               data=jsonutils.dumps(data),
                               content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_post_internal_with_incorrect_data(self):
        data = {
            "playbook_id": "1",
            "play_id": "one",
            "file_id": "False",
            "name": 1,
            "action": None,
            "lineno": "two",
            "tags": "None",
            "started": False
        }

        res = TaskApi().post(data)
        self.assertEqual(res.status_code, 400)

    def test_post_http_with_missing_argument(self):
        data = {
            "name": "Task from unit tests",
            "action": "debug",
            "lineno": 1,
            "tags": ['one', 'two'],
            "started": "1970-08-14T00:52:49.570031"
        }
        res = self.client.post('/api/v1/tasks/',
                               data=jsonutils.dumps(data),
                               content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_post_internal_with_missing_argument(self):
        data = {
            "name": "Task from unit tests",
            "action": "debug",
            "lineno": 1,
            "tags": ['one', 'two'],
            "started": "1970-08-14T00:52:49.570031"
        }
        res = TaskApi().post(data)
        self.assertEqual(res.status_code, 400)

    def test_post_http_with_nonexistant_play(self):
        ansible_run()
        data = {
            "play_id": 9001,
            "file_id": 1,
            "name": "Task from unit tests",
            "action": "debug",
            "lineno": 1,
            "tags": ['one', 'two'],
            "started": "1970-08-14T00:52:49.570031"
        }
        res = self.client.post('/api/v1/tasks/',
                               data=jsonutils.dumps(data),
                               content_type='application/json')
        self.assertEqual(res.status_code, 404)

    def test_post_internal_with_nonexistant_play(self):
        ansible_run()
        data = {
            "play_id": 9001,
            "file_id": 1,
            "name": "Task from unit tests",
            "action": "debug",
            "lineno": 1,
            "tags": ['one', 'two'],
            "started": "1970-08-14T00:52:49.570031"
        }
        res = TaskApi().post(data)
        self.assertEqual(res.status_code, 404)

    def test_post_http_with_nonexistant_file(self):
        ansible_run()
        data = {
            "play_id": 1,
            "file_id": 9001,
            "name": "Task from unit tests",
            "action": "debug",
            "lineno": 1,
            "tags": ['one', 'two'],
            "started": "1970-08-14T00:52:49.570031"
        }
        res = self.client.post('/api/v1/tasks/',
                               data=jsonutils.dumps(data),
                               content_type='application/json')
        self.assertEqual(res.status_code, 404)

    def test_post_internal_with_nonexistant_file(self):
        ansible_run()
        data = {
            "play_id": 1,
            "file_id": 9001,
            "name": "Task from unit tests",
            "action": "debug",
            "lineno": 1,
            "tags": ['one', 'two'],
            "started": "1970-08-14T00:52:49.570031"
        }
        res = TaskApi().post(data)
        self.assertEqual(res.status_code, 404)

    ###########
    # PATCH
    ###########
    def test_patch_http_redirect(self):
        res = self.client.patch('/api/v1/tasks')
        self.assertEqual(res.status_code, 301)

    def test_patch_http_with_no_data(self):
        res = self.client.patch('/api/v1/tasks/',
                                content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_patch_internal_with_no_data(self):
        res = TaskApi().patch()
        self.assertEqual(res.status_code, 400)

    def test_patch_http_existing(self):
        # Generate fake playbook data
        ctx = ansible_run()
        self.assertEqual(ctx['task'].id, 1)

        # We'll update the name field, assert we are actually
        # making a change
        new_name = "Updated task name"
        self.assertNotEqual(ctx['task'].name, new_name)

        data = {
            "id": ctx['task'].id,
            "name": new_name
        }
        res = self.client.patch('/api/v1/tasks/',
                                data=jsonutils.dumps(data),
                                content_type='application/json')
        self.assertEqual(res.status_code, 200)

        # The patch endpoint should return the full updated object
        data = jsonutils.loads(res.data)
        self.assertEqual(data['name'], new_name)

        # Confirm by re-fetching task
        updated = self.client.get('/api/v1/tasks/',
                                  content_type='application/json',
                                  query_string=dict(id=ctx['task'].id))
        updated_task = jsonutils.loads(updated.data)
        self.assertEqual(updated_task['name'], new_name)

    def test_patch_internal_existing(self):
        # Generate fake playbook data
        ctx = ansible_run()
        self.assertEqual(ctx['task'].id, 1)

        # We'll update the name field, assert we are actually
        # making a change
        new_name = "Updated task name"
        self.assertNotEqual(ctx['task'].name, new_name)

        data = {
            "id": ctx['task'].id,
            "name": new_name
        }
        res = TaskApi().patch(data)
        self.assertEqual(res.status_code, 200)

        # The patch endpoint should return the full updated object
        data = jsonutils.loads(res.data)
        self.assertEqual(data['name'], new_name)

        # Confirm by re-fetching play
        updated = TaskApi().get(id=ctx['task'].id)
        updated_task = jsonutils.loads(updated.data)
        self.assertEqual(updated_task['name'], new_name)

    def test_patch_http_with_missing_arg(self):
        ansible_run()
        data = {
            "name": "Updated task name"
        }
        res = self.client.patch('/api/v1/tasks/',
                                data=jsonutils.dumps(data),
                                content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_patch_internal_with_missing_arg(self):
        ansible_run()
        data = {
            "name": "Updated task name"
        }
        res = TaskApi().patch(data)
        self.assertEqual(res.status_code, 400)

    ###########
    # PUT
    ###########
    def test_put_http_redirect(self):
        # TODO: Does this raise a RequestRedirect due to underlying 405 ?
        with pytest.raises(RequestRedirect):
            self.client.put('/api/v1/tasks')

    # Not implemented yet
    def test_put_http_unimplemented(self):
        res = self.client.put('/api/v1/tasks/')
        self.assertEqual(res.status_code, 405)

    def test_put_internal_unimplemented(self):
        http = self.client.put('/api/v1/tasks/')
        internal = TaskApi().put()
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    ###########
    # DELETE
    ###########
    def test_delete_http_redirect(self):
        # TODO: Does this raise a RequestRedirect due to underlying 405 ?
        with pytest.raises(RequestRedirect):
            self.client.delete('/api/v1/tasks')

    # Not implemented yet
    def test_delete_http_unimplemented(self):
        res = self.client.delete('/api/v1/tasks/')
        self.assertEqual(res.status_code, 405)

    def test_delete_internal_unimplemented(self):
        http = self.client.delete('/api/v1/tasks/')
        internal = TaskApi().delete()
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    ###########
    # GET
    ###########
    def test_get_http_redirect(self):
        res = self.client.get('/api/v1/tasks',
                              content_type='application/json')
        self.assertEqual(res.status_code, 301)

    def test_get_http_with_bad_params_404_help(self):
        res = self.client.get('/api/v1/tasks/',
                              content_type='application/json',
                              query_string=dict(id=0))
        self.assertEqual(res.status_code, 404)
        # TODO: Improve this
        self.assertTrue(b'result_output' in res.data)
        self.assertTrue(b'query_parameters' in res.data)

    def test_get_internal_with_bad_params_404_help(self):
        http = self.client.get('/api/v1/tasks/',
                               content_type='application/json',
                               query_string=dict(id=0))
        internal = TaskApi().get(id=0)
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    def test_get_http_without_parameters_and_data(self):
        res = self.client.get('/api/v1/tasks/',
                              content_type='application/json')
        self.assertEqual(res.status_code, 404)
        # TODO: Improve this
        self.assertTrue(b'result_output' in res.data)
        self.assertTrue(b'query_parameters' in res.data)

    def test_get_internal_without_parameters_and_data(self):
        http = self.client.get('/api/v1/tasks/',
                               content_type='application/json')
        internal = TaskApi().get()
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    def test_get_http_without_parameters(self):
        ctx = ansible_run()
        res = self.client.get('/api/v1/tasks/',
                              content_type='application/json')
        self.assertEqual(res.status_code, 200)

        data = jsonutils.loads(res.data)[2]

        self.assertEqual(ctx['task'].id,
                         data['id'])
        self.assertEqual(ctx['task'].playbook_id,
                         data['playbook']['id'])
        self.assertEqual(ctx['task'].play_id,
                         data['play']['id'])
        self.assertEqual(ctx['task'].file_id,
                         data['file']['id'])
        self.assertEqual(ctx['task'].name,
                         data['name'])
        self.assertEqual(ctx['task'].action,
                         data['action'])
        self.assertEqual(ctx['task'].lineno,
                         data['lineno'])
        self.assertEqual(ctx['task'].tags,
                         data['tags'])
        self.assertEqual(ctx['task'].handler,
                         data['handler'])
        self.assertEqual(ctx['task'].started.isoformat(),
                         data['started'])
        self.assertEqual(ctx['task'].ended.isoformat(),
                         data['ended'])
        self.assertEqual(len(ctx['task'].results.all()),
                         len(data['results']))

    def test_get_internal_without_parameters(self):
        ansible_run()
        http = self.client.get('/api/v1/tasks/',
                               content_type='application/json')
        internal = TaskApi().get()
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    def test_get_http_with_id_parameter(self):
        ctx = ansible_run()

        res = self.client.get('/api/v1/tasks/',
                              content_type='application/json',
                              query_string=dict(id=1))
        self.assertEqual(res.status_code, 200)

        data = jsonutils.loads(res.data)
        self.assertEqual(ctx['task'].id,
                         data['id'])
        self.assertEqual(ctx['task'].playbook_id,
                         data['playbook']['id'])
        self.assertEqual(ctx['task'].play_id,
                         data['play']['id'])
        self.assertEqual(ctx['task'].file_id,
                         data['file']['id'])
        self.assertEqual(ctx['task'].name,
                         data['name'])
        self.assertEqual(ctx['task'].action,
                         data['action'])
        self.assertEqual(ctx['task'].lineno,
                         data['lineno'])
        self.assertEqual(ctx['task'].tags,
                         data['tags'])
        self.assertEqual(ctx['task'].handler,
                         data['handler'])
        self.assertEqual(ctx['task'].started.isoformat(),
                         data['started'])
        self.assertEqual(ctx['task'].ended.isoformat(),
                         data['ended'])
        self.assertEqual(len(ctx['task'].results.all()),
                         len(data['results']))

    def test_get_internal_with_id_parameter(self):
        ansible_run()
        # Run twice to get a second playbook
        ansible_run()
        playbooks = models.Playbook.query.all()
        self.assertEqual(len(playbooks), 2)

        http = self.client.get('/api/v1/tasks/',
                               content_type='application/json',
                               query_string=dict(id=1))
        internal = TaskApi().get(id=1)
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    def test_get_http_with_id_url(self):
        ctx = ansible_run()

        res = self.client.get('/api/v1/tasks/1',
                              content_type='application/json')
        self.assertEqual(res.status_code, 200)

        data = jsonutils.loads(res.data)
        self.assertEqual(ctx['task'].id,
                         data['id'])
        self.assertEqual(ctx['task'].playbook_id,
                         data['playbook']['id'])
        self.assertEqual(ctx['task'].play_id,
                         data['play']['id'])
        self.assertEqual(ctx['task'].file_id,
                         data['file']['id'])
        self.assertEqual(ctx['task'].name,
                         data['name'])
        self.assertEqual(ctx['task'].action,
                         data['action'])
        self.assertEqual(ctx['task'].lineno,
                         data['lineno'])
        self.assertEqual(ctx['task'].tags,
                         data['tags'])
        self.assertEqual(ctx['task'].handler,
                         data['handler'])
        self.assertEqual(ctx['task'].started.isoformat(),
                         data['started'])
        self.assertEqual(ctx['task'].ended.isoformat(),
                         data['ended'])
        self.assertEqual(len(ctx['task'].results.all()),
                         len(data['results']))

    def test_get_internal_with_id_url(self):
        ansible_run()
        # Run twice to get a second playbook
        ansible_run()
        playbooks = models.Playbook.query.all()
        self.assertEqual(len(playbooks), 2)

        http = self.client.get('/api/v1/tasks/1',
                               content_type='application/json')
        internal = TaskApi().get(id=1)
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)
