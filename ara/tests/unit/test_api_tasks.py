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

from ara.api.tasks import TaskApi
from ara.api.v1.tasks import (
    BASE_FIELDS,
    TASK_FIELDS
)


def test_bootstrap(run_ansible_env):
    # This just takes care of initializing run_ansible_env which runs once
    pass


###########
# GET
###########
def test_get_not_found(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = TaskApi().get(id=9001)
    assert resp.status_code == 404
    assert 'query_parameters' in data['help']
    assert 'result_output' in data['help']
    assert "Task 9001 doesn't exist" in data['message']


def test_get_list(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = TaskApi().get()
    assert resp.status_code == 200
    assert isinstance(data, list)
    assert data[0]['id'] == 1
    assert data[0]['href'] == '/api/v1/tasks/1'
    for key in BASE_FIELDS.keys():
        assert key in data[0]


def test_get_id(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = TaskApi().get(id=1)
    assert resp.status_code == 200
    assert data['id'] == 1
    assert data['href'] == '/api/v1/tasks/1'
    assert data['name'] == 'Gathering Facts'
    assert data['action'] == 'setup'
    assert data['tags'] == ['always']
    assert not data['handler']
    assert data['results'] == '/api/v1/tasks/1/results'

    assert data['playbook']['id'] == 1
    assert data['playbook']['href'] == '/api/v1/playbooks/1'
    assert data['play']['id'] == 1
    assert data['play']['href'] == '/api/v1/plays/1'
    assert data['file']['id'] == 2
    assert data['file']['href'] == '/api/v1/files/2'

    for key in TASK_FIELDS.keys():
        assert key in data


def test_get_by_playbook_id(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = TaskApi().get(playbook_id=1)
    assert resp.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 8
    assert data[0]['id'] == 1
    assert data[0]['href'] == '/api/v1/tasks/1'
    for key in BASE_FIELDS.keys():
        assert key in data[0]


def test_get_by_play_id(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE',
                       run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = TaskApi().get(play_id=1)
    assert resp.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 4
    assert data[0]['id'] == 1
    assert data[0]['href'] == '/api/v1/tasks/1'
    for key in BASE_FIELDS.keys():
        assert key in data[0]


###########
# POST
###########
def test_post_with_no_data(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = TaskApi().post()
    assert resp.status_code == 400


def test_post_with_correct_data(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    # Get the number of tasks in the play before adding a new task
    resp, before = TaskApi().get(play_id=1)
    assert resp.status_code == 200

    resp, data = TaskApi().post(
        play_id=1,
        file_id=2,
        name='Task from unit tests',
        action='debug',
        lineno=1,
        tags=['one', 'two'],
        started='1970-08-14T00:52:49.570031'
    )
    assert resp.status_code == 200

    # Confirm that the POST returned the full task object ("data")
    # and that the task was really created properly by fetching it
    # ("task")
    resp, task = TaskApi().get(id=data['id'])
    assert resp.status_code == 200
    assert task == data

    # Assert that we now have more tasks
    resp, after = TaskApi().get(play_id=1)
    assert resp.status_code == 200
    assert len(before) < len(after)

    # Assert that the data is correct
    assert task['href'] == '/api/v1/tasks/%s' % task['id']
    assert task['name'] == 'Task from unit tests'
    assert task['action'] == 'debug'
    assert task['lineno'] == 1
    assert task['tags'] == ['one', 'two']
    assert not task['handler']
    assert task['started'] == '1970-08-14T00:52:49.570031'
    assert task['results'] == '/api/v1/tasks/%s/results' % task['id']

    assert task['playbook']['id'] == 1
    assert task['playbook']['href'] == '/api/v1/playbooks/1'
    assert task['play']['id'] == 1
    assert task['play']['href'] == '/api/v1/plays/1'
    assert task['file']['id'] == 2
    assert task['file']['href'] == '/api/v1/files/2'


def test_post_with_incorrect_data(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = TaskApi().post(
        play_id='one',
        file_id='False',
        name=1,
        action=None,
        lineno='two',
        tags='None',
        started=False
    )
    assert resp.status_code == 400


def test_post_with_missing_argument(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = TaskApi().post(
        name='Task from unit tests',
        action='debug',
        lineno=1,
        tags=['one', 'two'],
        started='1970-08-14T00:52:49.570031'
    )
    assert resp.status_code == 400


def test_post_with_nonexistant_play(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = TaskApi().post(
        play_id=9001,
        file_id=1,
        name='Task from unit tests',
        action='debug',
        lineno=1,
        tags=['one', 'two'],
        started='1970-08-14T00:52:49.570031'
    )
    assert resp.status_code == 404


def test_post_with_nonexistant_file(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = TaskApi().post(
        play_id=1,
        file_id=9001,
        name='Task from unit tests',
        action='debug',
        lineno=1,
        tags=['one', 'two'],
        started='1970-08-14T00:52:49.570031'
    )
    assert resp.status_code == 404


###########
# PATCH
###########
def test_patch_with_no_data(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = TaskApi().patch()
    assert resp.status_code == 400


def test_patch_existing(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    # Get existing task
    resp, task = TaskApi().get(id=1)
    assert resp.status_code == 200

    # We'll update the name field, assert we are actually
    # making a change
    new_name = "Updated task name"
    assert task['name'] != new_name

    resp, data = TaskApi().patch(
        id=task['id'],
        name=new_name
    )
    assert resp.status_code == 200

    # The patch endpoint should return the full updated object
    assert data['name'] == new_name

    # Confirm by re-fetching task
    resp, updated = TaskApi().get(id=task['id'])
    assert resp.status_code == 200
    assert updated['name'] == new_name
    assert data == updated


def test_patch_with_missing_arg(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = TaskApi().patch(
        name='Updated task name'
    )
    assert resp.status_code == 400


###########
# PUT
###########
def test_put_unimplemented(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = TaskApi().put()
    assert resp.status_code == 405


###########
# DELETE
###########
def test_delete_unimplemented(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = TaskApi().delete()
    assert resp.status_code == 405
