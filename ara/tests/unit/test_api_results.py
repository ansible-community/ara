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

from ara.api.results import ResultApi
from ara.api.v1.results import (
    BASE_FIELDS,
    RESULT_FIELDS
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

    resp, data = ResultApi().get(id=9001)
    assert resp.status_code == 404
    assert 'query_parameters' in data['help']
    assert 'result_output' in data['help']
    assert "Result 9001 doesn't exist" in data['message']


def test_get_list(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = ResultApi().get()
    assert resp.status_code == 200
    assert isinstance(data, list)
    assert data[0]['id'] == 1
    assert data[0]['href'] == '/api/v1/results/1'
    for key in BASE_FIELDS.keys():
        assert key in data[0]


def test_get_id(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = ResultApi().get(id=1)
    assert resp.status_code == 200
    assert data['id'] == 1
    assert data['href'] == '/api/v1/results/1'
    assert data['status'] == 'ok'
    assert not data['changed']
    assert not data['failed']
    assert not data['skipped']
    assert not data['unreachable']
    assert not data['ignore_errors']

    assert data['playbook']['id'] == 1
    assert data['playbook']['href'] == '/api/v1/playbooks/1'
    assert data['play']['id'] == 1
    assert data['play']['href'] == '/api/v1/plays/1'
    assert data['task']['id'] == 1
    assert data['task']['href'] == '/api/v1/tasks/1'
    assert data['host']['id'] == 1
    assert data['host']['href'] == '/api/v1/hosts/1'

    for key in RESULT_FIELDS.keys():
        assert key in data


def test_get_by_playbook_id(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = ResultApi().get(playbook_id=1)
    assert resp.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 16
    assert data[0]['id'] == 1
    assert data[0]['href'] == '/api/v1/results/1'
    for key in BASE_FIELDS.keys():
        assert key in data[0]


def test_get_by_play_id(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE',
                       run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = ResultApi().get(play_id=1)
    assert resp.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 4
    assert data[0]['id'] == 1
    assert data[0]['href'] == '/api/v1/results/1'
    for key in BASE_FIELDS.keys():
        assert key in data[0]


def test_get_by_task_id(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE',
                       run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = ResultApi().get(task_id=1)
    assert resp.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['id'] == 1
    assert data[0]['href'] == '/api/v1/results/1'
    for key in BASE_FIELDS.keys():
        assert key in data[0]


def test_get_by_host_id(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE',
                       run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = ResultApi().get(host_id=1)
    assert resp.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 8
    assert data[0]['id'] == 1
    assert data[0]['href'] == '/api/v1/results/1'
    for key in BASE_FIELDS.keys():
        assert key in data[0]


###########
# POST
###########
def test_post_with_no_data(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = ResultApi().post()
    assert resp.status_code == 400


def test_post_with_correct_data(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    # Get the number of results in the task before adding a new result
    resp, before = ResultApi().get(task_id=1)
    assert resp.status_code == 200

    resp, result = ResultApi().post(
        host_id=1,
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
    assert resp.status_code == 200

    # Confirm that the POST returned the full result object ("data")
    # and that the result was really created properly by fetching it
    # ("result")
    resp, data = ResultApi().get(id=result['id'])
    assert resp.status_code == 200
    assert result == data

    # Assert that we now have more plays
    resp, after = ResultApi().get(task_id=1)
    assert resp.status_code == 200
    assert len(before) < len(after)

    # Assert that the data is correct
    assert result['href'] == '/api/v1/results/%s' % result['id']
    assert result['status'] == 'ok'
    assert result['changed']
    assert not result['failed']
    assert not result['skipped']
    assert not result['unreachable']
    assert not result['ignore_errors']
    assert result['result']['msg'] == 'some result'
    assert result['started'] == '1970-08-14T00:52:49.570031'

    assert result['playbook']['id'] == 1
    assert result['playbook']['href'] == '/api/v1/playbooks/1'
    assert result['play']['id'] == 1
    assert result['play']['href'] == '/api/v1/plays/1'
    assert result['task']['id'] == 1
    assert result['task']['href'] == '/api/v1/tasks/1'
    assert result['host']['id'] == 1
    assert result['host']['href'] == '/api/v1/hosts/1'


def test_post_with_incorrect_data(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = ResultApi().post(
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
    assert resp.status_code == 400


def test_post_with_missing_argument(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = ResultApi().post(
        status='ok',
        changed=True,
        failed=False,
        skipped=False,
        unreachable=False,
        ignore_errors=False,
        result={'msg': 'some result'},
        started='1970-08-14T00:52:49.570031'
    )
    assert resp.status_code == 400


def test_post_with_nonexistant_host(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = ResultApi().post(
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
    assert resp.status_code == 404


def test_post_with_nonexistant_task(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = ResultApi().post(
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
    assert resp.status_code == 404


###########
# PATCH
###########
def test_patch_with_no_data(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = ResultApi().patch()
    assert resp.status_code == 400


def test_patch_existing(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    # Get existing result
    resp, result = ResultApi().get(id=1)
    assert resp.status_code == 200

    # We'll update the status field, assert we are actually
    # making a change
    new_status = 'failed'
    assert result['status'] != new_status

    resp, data = ResultApi().patch(
        id=result['id'],
        status=new_status
    )
    assert resp.status_code == 200

    # The patch endpoint should return the full updated object
    assert data['status'] == new_status

    # Confirm by re-fetching result
    resp, updated = ResultApi().get(id=result['id'])
    assert resp.status_code == 200
    assert updated['status'] == new_status
    assert data == updated


def test_patch_with_missing_arg(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = ResultApi().patch(
        status='failed'
    )
    assert resp.status_code == 400


###########
# PUT
###########
def test_put_unimplemented(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = ResultApi().put()
    assert resp.status_code == 405


###########
# DELETE
###########
def test_delete_unimplemented(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = ResultApi().delete()
    assert resp.status_code == 405
