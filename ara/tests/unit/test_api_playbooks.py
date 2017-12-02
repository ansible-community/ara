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

from ansible import __version__ as ansible_version
from ara.api.playbooks import PlaybookApi
from ara.api.v1.playbooks import (
    BASE_FIELDS,
    PLAYBOOK_FIELDS
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

    resp, data = PlaybookApi().get(id=9001)
    assert resp.status_code == 404
    assert 'query_parameters' in data['help']
    assert 'result_output' in data['help']
    assert "Playbook 9001 doesn't exist" in data['message']


def test_get_list(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = PlaybookApi().get()
    assert resp.status_code == 200
    assert isinstance(data, list)
    assert data[0]['id'] == 1
    assert data[0]['href'] == '/api/v1/playbooks/1'
    for key in BASE_FIELDS.keys():
        assert key in data[0]


def test_get_id(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = PlaybookApi().get(id=1)
    assert resp.status_code == 200
    assert data['id'] == 1
    assert data['href'] == '/api/v1/playbooks/1'
    assert data['completed']
    assert data['ansible_version'] == ansible_version
    assert data['path'] == run_ansible_env['playbook']
    assert run_ansible_env['inventory'] in data['parameters']['inventory']

    assert data['hosts'] == '/api/v1/playbooks/1/hosts'
    assert data['files'] == '/api/v1/playbooks/1/files'
    assert data['plays'] == '/api/v1/playbooks/1/plays'
    assert data['records'] == '/api/v1/playbooks/1/records'
    assert data['results'] == '/api/v1/playbooks/1/results'
    assert data['tasks'] == '/api/v1/playbooks/1/tasks'

    for key in PLAYBOOK_FIELDS.keys():
        assert key in data


###########
# POST
###########
def test_post_with_no_data(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = PlaybookApi().post()
    assert resp.status_code == 400


def test_post_with_correct_data(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    # Get the number of playbooks before adding a new playbook
    resp, before = PlaybookApi().get()
    assert resp.status_code == 200

    # Assert that we only have one playbook
    resp, playbooks = PlaybookApi().get()
    assert resp.status_code == 200
    assert len(playbooks) == 1

    # Create a new playbook
    resp, data = PlaybookApi().post(
        path='/root/playbook.yml',
        ansible_version='2.4.2.0',
        parameters={
            'become': True,
            'become_user': 'root'
        },
        completed=False,
        started='1970-08-14T00:52:49.570031'
    )
    assert resp.status_code == 200

    # Confirm that the POST returned the full playbook object ("data")
    # and that the playbook was really created properly by fetching it
    # ("playbook")
    resp, playbook = PlaybookApi().get(id=data['id'])
    assert resp.status_code == 200
    assert data == playbook

    # Assert that we now have more playbooks
    resp, after = PlaybookApi().get()
    assert resp.status_code == 200
    assert len(before) < len(after)

    # Assert that the data is correct
    assert not playbook['completed']
    assert playbook['id'] == 2
    assert playbook['href'] == '/api/v1/playbooks/%s' % playbook['id']
    assert playbook['ansible_version'] == '2.4.2.0'
    assert data['path'] == '/root/playbook.yml'

    assert data['hosts'] == '/api/v1/playbooks/%s/hosts' % playbook['id']
    assert data['files'] == '/api/v1/playbooks/%s/files' % playbook['id']
    assert data['plays'] == '/api/v1/playbooks/%s/plays' % playbook['id']
    assert data['records'] == '/api/v1/playbooks/%s/records' % playbook['id']
    assert data['results'] == '/api/v1/playbooks/%s/results' % playbook['id']
    assert data['tasks'] == '/api/v1/playbooks/%s/tasks' % playbook['id']


def test_post_with_incorrect_data(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = PlaybookApi().post(
        path=False,
        ansible_version=2,
        parameters=['one'],
        completed='yes',
        started='a long time ago'
    )
    assert resp.status_code == 400


def test_post_with_missing_argument(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = PlaybookApi().post(
        path='/root/playbook.yml'
    )
    assert resp.status_code == 400


###########
# PATCH
###########
def test_patch_with_no_data(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = PlaybookApi().patch()
    assert resp.status_code == 400


def test_patch_existing(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    # Get the existing playbook
    resp, playbook = PlaybookApi().get(id=1)
    assert resp.status_code == 200

    # We'll update the ansible_version field, assert we are actually
    # making a change
    new_version = "9.0.0.1"
    assert playbook['ansible_version'] != new_version

    resp, data = PlaybookApi().patch(
        id=playbook['id'],
        ansible_version=new_version
    )
    assert resp.status_code == 200

    # The patch endpoint should return the full updated object
    assert data['ansible_version'] == new_version

    # Confirm by re-fetching playbook
    resp, updated = PlaybookApi().get(id=1)
    assert resp.status_code == 200
    assert data == updated


def test_patch_with_missing_arg(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = PlaybookApi().patch(
        ansible_version='1.9.9.6'
    )
    assert resp.status_code == 400


###########
# PUT
###########
def test_put_unimplemented(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = PlaybookApi().put()
    assert resp.status_code == 405


###########
# DELETE
###########
def test_delete_unimplemented(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = PlaybookApi().delete()
    assert resp.status_code == 405
