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

import os
from ansible import __version__ as ansible_version
from ara.api.playbooks import PlaybookApi


def test_bootstrap(run_ansible_env):
    # This just takes care of initializing run_ansible_env which runs once
    assert 'ARA_DATABASE' not in os.environ
    assert 'ARA_DIR' not in os.environ

###########
# GET
###########


def test_empty_database(monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', 'sqlite://')
    resp, data = PlaybookApi().get()
    assert resp.status_code == 404


def test_get_playbook_not_found(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = PlaybookApi().get(id=9001)
    assert resp.status_code == 404
    assert 'query_parameters' in data['help']
    assert 'result_output' in data['help']
    assert "Playbook 9001 doesn't exist" in data['message']


def test_get_playbook_id(run_ansible_env, monkeypatch):
    # These need to be persisted to be carried over to the tests
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = PlaybookApi().get(id=1)
    assert resp.status_code == 200
    assert data['completed']
    assert data['id'] == 1
    assert data['href'] == '/api/v1/playbooks/1'
    assert data['ansible_version'] == ansible_version
    assert data['path'] == run_ansible_env['playbook']
    assert run_ansible_env['inventory'] in data['parameters']['inventory']

    assert data['hosts'] == '/api/v1/playbooks/1/hosts'
    assert data['files'] == '/api/v1/playbooks/1/files'
    assert data['plays'] == '/api/v1/playbooks/1/plays'
    assert data['records'] == '/api/v1/playbooks/1/records'
    assert data['results'] == '/api/v1/playbooks/1/results'
    assert data['tasks'] == '/api/v1/playbooks/1/tasks'

    assert 'started' in data
    assert 'ended' in data
