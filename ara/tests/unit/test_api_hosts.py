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

from ara.api.hosts import HostApi
from ara.api.v1.hosts import (
    BASE_FIELDS,
    HOST_FIELDS
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

    resp, data = HostApi().get(id=9001)
    assert resp.status_code == 404
    assert 'query_parameters' in data['help']
    assert 'result_output' in data['help']
    assert "Host 9001 doesn't exist" in data['message']


def test_get_list(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = HostApi().get()
    assert resp.status_code == 200
    assert isinstance(data, list)
    assert data[0]['id'] == 1
    assert data[0]['href'] == '/api/v1/hosts/1'
    for key in BASE_FIELDS.keys():
        assert key in data[0]


def test_get_id(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = HostApi().get(id=1)
    assert resp.status_code == 200
    assert data['id'] == 1
    assert data['href'] == '/api/v1/hosts/1'
    assert data['name'] == 'localhost'
    assert data['playbook']['id'] == 1
    assert data['playbook']['href'] == '/api/v1/playbooks/1'

    assert isinstance(data['changed'], int)
    assert isinstance(data['failed'], int)
    assert isinstance(data['ok'], int)
    assert isinstance(data['skipped'], int)
    assert isinstance(data['unreachable'], int)

    for key in HOST_FIELDS.keys():
        assert key in data


def test_get_by_playbook_id(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = HostApi().get(playbook_id=1)
    assert resp.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 5
    assert data[0]['id'] == 1
    assert data[0]['href'] == '/api/v1/hosts/1'
    for key in BASE_FIELDS.keys():
        assert key in data[0]


###########
# POST
###########
def test_post_with_no_data(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = HostApi().post()
    assert resp.status_code == 400


def test_post_with_correct_data(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    # Get the number of hosts in the playbook before adding a new host
    resp, before = HostApi().get(playbook_id=1)
    assert resp.status_code == 200

    # Create a host in an existing playbook
    resp, host = HostApi().post(
        playbook_id=1,
        name='test_hostname',
        facts={'ansible_foo': 'bar'},
        changed=1,
        failed=0,
        ok=4,
        skipped=1,
        unreachable=0
    )
    assert resp.status_code == 200

    # Confirm that the POST returned the full host object ("data")
    # and that the host was really created properly by fetching it
    # ("host")
    resp, data = HostApi().get(id=host['id'])
    assert resp.status_code == 200
    assert data == host

    # Assert that we now have more hosts
    resp, after = HostApi().get(playbook_id=1)
    assert resp.status_code == 200
    assert len(before) < len(after)

    # Assert that the data is correct
    assert host['href'] == '/api/v1/hosts/%s' % host['id']
    assert host['name'] == 'test_hostname'
    assert host['facts']['ansible_foo'] == 'bar'
    assert host['changed'] == 1
    assert host['failed'] == 0
    assert host['ok'] == 4
    assert host['skipped'] == 1
    assert host['unreachable'] == 0

    assert host['playbook']['id'] == 1
    assert host['playbook']['href'] == '/api/v1/playbooks/1'


def test_post_with_incorrect_data(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = HostApi().post(
        playbook_id='1',
        name=1,
        facts=False,
    )
    assert resp.status_code == 400


def test_post_with_missing_argument(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = HostApi().post(name='hostname')
    assert resp.status_code == 400


def test_post_with_nonexistant_host(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = HostApi().post(
        playbook_id=9001,
        name='hostname'
    )
    assert resp.status_code == 404


def test_post_already_exists(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    # Retrieve a host so we can post the same thing
    resp, host = HostApi().get(id=1)
    assert resp.status_code == 200

    resp, data = HostApi().post(
        playbook_id=host['playbook']['id'],
        name=host['name'],
        facts=host['facts'],
        changed=host['changed'],
        failed=host['failed'],
        ok=host['ok'],
        skipped=host['skipped'],
        unreachable=host['unreachable']
    )
    assert resp.status_code == 200
    # Posting a host that already exists doesn't create a new host
    assert data == host


###########
# PATCH
###########
def test_patch_with_no_data(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = HostApi().patch()
    assert resp.status_code == 400


def test_patch_existing(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    # Get existing host
    resp, host = HostApi().get(id=1)
    assert resp.status_code == 200

    # We'll update the name field, assert we are actually
    # making a change
    new_name = "Updated_hostname"
    assert host['name'] != new_name

    resp, data = HostApi().patch(
        id=host['id'],
        name=new_name
    )
    assert resp.status_code == 200

    # The patch endpoint should return the full updated object
    assert data['name'] == new_name

    # Confirm by re-fetching host
    resp, updated = HostApi().get(id=1)
    assert resp.status_code == 200
    assert data == updated


def test_patch_with_missing_arg(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = HostApi().patch(
        name='Updated_hostname'
    )
    assert resp.status_code == 400


###########
# PUT
###########
def test_put_unimplemented(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = HostApi().put()
    assert resp.status_code == 405


###########
# DELETE
###########
def test_delete_unimplemented(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = HostApi().delete()
    assert resp.status_code == 405
