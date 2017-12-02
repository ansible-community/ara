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

from ara.api.records import RecordApi
from ara.api.v1.records import (
    BASE_FIELDS,
    RECORD_FIELDS
)


# We want to run ara-functional.yml to run ara_record and ara_read tasks.
def pytest_generate_tests(metafunc):
    if 'run_ansible_env' in metafunc.fixturenames:
        metafunc.parametrize('run_ansible_env',
                             [({'playbook': 'ara-functional.yml'})],
                             indirect=True, scope='module')


def test_bootstrap(run_ansible_env):
    # This just takes care of initializing run_ansible_env which runs once
    pass


###########
# GET
###########
def test_get_not_found(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = RecordApi().get(id=9001)
    assert resp.status_code == 404
    assert 'query_parameters' in data['help']
    assert 'result_output' in data['help']
    assert "Record 9001 doesn't exist" in data['message']


def test_get_list(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = RecordApi().get()
    assert resp.status_code == 200
    assert isinstance(data, list)
    assert data[0]['id'] == 1
    assert data[0]['href'] == '/api/v1/records/1'
    for key in BASE_FIELDS.keys():
        assert key in data[0]


def test_get_id(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = RecordApi().get(id=1)
    assert resp.status_code == 200
    assert data['id'] == 1
    assert data['href'] == '/api/v1/records/1'
    assert data['playbook']['id'] == 1
    assert data['playbook']['href'] == '/api/v1/playbooks/1'

    for key in RECORD_FIELDS.keys():
        assert key in data


def test_get_by_playbook_id(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = RecordApi().get(playbook_id=1)
    assert resp.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 6
    assert data[0]['id'] == 1
    assert data[0]['href'] == '/api/v1/records/1'
    for key in BASE_FIELDS.keys():
        assert key in data[0]


###########
# POST
###########
def test_post_with_no_data(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = RecordApi().post()
    assert resp.status_code == 400


def test_post_with_correct_data(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    # Get the number of records in the playbook before adding a new record
    resp, before = RecordApi().get(playbook_id=1)
    assert resp.status_code == 200

    resp, data = RecordApi().post(
        playbook_id=1,
        key='unit_key',
        value='unit_value',
        type='text'
    )
    assert resp.status_code == 200

    # Confirm that the POST returned the full record object ("data")
    # and that the record was really created properly by fetching it
    # ("record")
    resp, record = RecordApi().get(id=data['id'])
    assert resp.status_code == 200
    assert data == record

    # Assert that we now have more records
    resp, after = RecordApi().get(playbook_id=1)
    assert resp.status_code == 200
    assert len(before) < len(after)

    # Assert that the data is correct
    assert record['href'] == '/api/v1/records/%s' % record['id']
    assert record['key'] == 'unit_key'
    assert record['value'] == 'unit_value'
    assert record['type'] == 'text'

    assert record['playbook']['id'] == 1
    assert record['playbook']['href'] == '/api/v1/playbooks/1'


def test_post_with_incorrect_data(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = RecordApi().post(
        playbook_id='1',
        key=1,
        value=False,
        type='binary'
    )
    assert resp.status_code == 400


def test_post_with_missing_argument(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = RecordApi().post(
        key='foo',
        value='bar',
        type='text'
    )
    assert resp.status_code == 400


def test_post_with_nonexistant_playbook(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = RecordApi().post(
        playbook_id=9001,
        key='foo',
        value='bar',
        type='text'
    )
    assert resp.status_code == 404


###########
# PATCH
###########
def test_patch_with_no_data(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = RecordApi().patch()
    assert resp.status_code == 400


def test_patch_existing(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    # Get existing record
    resp, record = RecordApi().get(id=1)
    assert resp.status_code == 200

    # We'll update the value field, assert we are actually
    # making a change
    new_value = "Updated value"
    assert record['value'] != new_value

    resp, data = RecordApi().patch(
        id=record['id'],
        value=new_value
    )
    assert resp.status_code == 200

    # The patch endpoint should return the full updated object
    assert data['value'] == new_value

    # Confirm by re-fetching record
    resp, updated = RecordApi().get(id=record['id'])
    assert resp.status_code == 200
    assert updated['value'] == new_value
    assert data == updated


def test_patch_with_missing_arg(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = RecordApi().patch(
        value='Updated value'
    )
    assert resp.status_code == 400


###########
# PUT
###########
def test_put_unimplemented(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = RecordApi().put()
    assert resp.status_code == 405


###########
# DELETE
###########
def test_delete_unimplemented(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = RecordApi().delete()
    assert resp.status_code == 405
