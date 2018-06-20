#!/usr/bin/env python
#  Copyright (c) 2018 Red Hat, Inc.
#
#  This file is part of ARA Records Ansible.
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

# A very basic script to smoke test that the Ansible integration is not
# horribly broken until we get something more robust in place.

from ara.clients.offline import AraOfflineClient


def validate_playbook(playbook):
    assert len(playbook['parameters']) == 40
    assert 'hacking/test-playbook.yml' in playbook['file']['path']
    assert len(playbook['files']) == 15
    assert playbook['completed']


def validate_play(play):
    assert play['completed']


def validate_task(task):
    assert task['completed']


def main():
    client = AraOfflineClient()

    playbooks = client.get('/api/v1/playbooks/')
    assert len(playbooks['results']) == 1
    assert playbooks['count'] == 1
    validate_playbook(playbooks['results'][0])

    playbook = client.get(
        '/api/v1/playbooks/%s/' % playbooks['results'][0]['id']
    )
    validate_playbook(playbook)

    plays = client.get('/api/v1/plays/')
    assert len(plays['results']) == 2
    assert plays['count'] == 2
    validate_play(plays['results'][0])

    play = client.get(
        '/api/v1/plays/%s/' % plays['results'][0]['id']
    )
    validate_play(play)

    tasks = client.get('/api/v1/tasks/')
    assert len(tasks['results']) == 8
    assert tasks['count'] == 8
    validate_task(tasks['results'][0])

    task = client.get(
        '/api/v1/tasks/%s/' % tasks['results'][0]['id']
    )
    validate_task(task)

    client.log.info('All assertions passed.')


if __name__ == "__main__":
    main()
