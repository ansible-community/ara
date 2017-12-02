# -*- coding: utf-8 -*-
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

from ara.api.files import FileApi
from ara.api.v1.files import (
    BASE_FIELDS,
    FILE_FIELDS
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

    resp, data = FileApi().get(id=9001)
    assert resp.status_code == 404
    assert 'query_parameters' in data['help']
    assert 'result_output' in data['help']
    assert "File 9001 doesn't exist" in data['message']


def test_get_list(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = FileApi().get()
    assert resp.status_code == 200
    assert isinstance(data, list)
    assert data[0]['id'] == 1
    assert data[0]['href'] == '/api/v1/files/1'
    for key in BASE_FIELDS.keys():
        assert key in data[0]


def test_get_id(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = FileApi().get(id=1)
    assert resp.status_code == 200
    assert data['id'] == 1
    assert data['href'] == '/api/v1/files/1'
    assert data['path'] == run_ansible_env['inventory']
    assert not data['is_playbook']
    assert data['playbook']['id'] == 1
    assert data['playbook']['href'] == '/api/v1/playbooks/1'

    for key in FILE_FIELDS.keys():
        assert key in data


def test_get_by_playbook_id(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = FileApi().get(playbook_id=1)
    assert resp.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 4
    assert data[0]['id'] == 1
    assert data[0]['href'] == '/api/v1/files/1'
    for key in BASE_FIELDS.keys():
        assert key in data[0]


###########
# POST
###########
def test_post_with_no_data(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = FileApi().post()
    assert resp.status_code == 400


def test_post_with_correct_data(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    # Get the number of files in the playbook before adding a new file
    resp, before = FileApi().get(playbook_id=1)
    assert resp.status_code == 200

    # Create fake playbook data and create a file in it
    resp, file_ = FileApi().post(
        playbook_id=1,
        path='/root/playbook.yml',
        content='---\n- name: Task from ünit tests'
    )
    assert resp.status_code == 200

    # Confirm that the POST returned the full file object ("data")
    # and that the file was really created properly by fetching it
    # ("file")
    resp, data = FileApi().get(id=file_['id'])
    assert resp.status_code == 200
    assert data == file_

    # Assert that we now have more files
    resp, after = FileApi().get(playbook_id=1)
    assert resp.status_code == 200
    assert len(before) < len(after)

    # Assert that the data is correct
    assert file_['href'] == '/api/v1/files/%s' % file_['id']
    assert file_['path'] == '/root/playbook.yml'
    assert file_['content'] == u'---\n- name: Task from ünit tests'

    assert file_['playbook']['id'] == 1
    assert file_['playbook']['href'] == '/api/v1/playbooks/1'


def test_post_with_incorrect_data(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = FileApi().post(
        playbook_id='1',
        path=False,
        content=1
    )
    assert resp.status_code == 400


def test_post_with_missing_argument(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = FileApi().post(
        path='/root/playbook.yml',
        content='hello world'
    )
    assert resp.status_code == 400


def test_post_with_nonexistant_playbook(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = FileApi().post(
        playbook_id=9001,
        path='/root/playbook.yml',
        content='hello world'
    )
    assert resp.status_code == 404


def test_post_file_already_exists(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    # Retrieve the playbook file so we can post the same thing
    resp, file_ = FileApi().get(id=1)
    assert resp.status_code == 200

    # Post the same thing
    resp, data = FileApi().post(
        playbook_id=file_['id'],
        path=file_['path'],
        content=file_['content']
    )
    assert resp.status_code == 200
    # Posting a file that already exists doesn't create a new file
    assert file_ == data


###########
# PATCH
###########
def test_patch_with_no_data(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = FileApi().patch()
    assert resp.status_code == 400


def test_patch_existing(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    # Get existing file
    resp, file_ = FileApi().get(id=1)
    assert resp.status_code == 200

    # We'll update the content field, assert we are actually
    # making a change
    new_content = '# Empty file !'
    assert file_['content'] != new_content

    resp, data = FileApi().patch(
        id=file_['id'],
        content=new_content
    )
    assert resp.status_code == 200

    # The patch endpoint should return the full updated object
    assert data['content'] == new_content

    # Confirm by re-fetching file
    resp, updated = FileApi().get(id=file_['id'])
    assert resp.status_code == 200
    assert updated['content'] == new_content


def test_patch_with_missing_arg(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = FileApi().patch(path='/updated/path.yml')
    assert resp.status_code == 400


###########
# PUT
###########
def test_put_unimplemented(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = FileApi().put()
    assert resp.status_code == 405


###########
# DELETE
###########
def test_delete_unimplemented(run_ansible_env, monkeypatch):
    monkeypatch.setenv('ARA_DATABASE', run_ansible_env['env']['ARA_DATABASE'])
    monkeypatch.setenv('ARA_DIR', run_ansible_env['env']['ARA_DIR'])

    resp, data = FileApi().delete()
    assert resp.status_code == 405
