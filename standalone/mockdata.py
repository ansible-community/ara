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

# Creates mock data offline leveraging the API
import django
import hashlib
import json
import os
import sys
from django.core import serializers

parent_directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parent_directory)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ara.settings')
django.setup()

from api import models
from django.test import Client


def post(endpoint, data):
    client = Client()
    print("Posting to %s..." % endpoint)
    obj = client.post(endpoint, data)
    print("HTTP %s" % obj.status_code)
    print("Got: %s" % json.dumps(obj.json(), indent=2))
    print("#" * 40)

    return obj


playbook = post(
    '/api/v1/playbooks/',
    dict(
        started='2016-05-06T17:20:25.749489-04:00',
        path='/tmp/playbook.yml',
        ansible_version='2.3.4',
        completed=False,
        parameters=json.dumps(dict(
            foo='bar'
        ))
    )
)

play = post(
    '/api/v1/plays/',
    dict(
        started='2016-05-06T17:20:25.749489-04:00',
        name='Test play',
        playbook=playbook.json()['url']
    )
)

playbook_file = post(
    '/api/v1/files/',
    dict(
        path=playbook.json()['path'],
        # TODO: Fix this somehow
        content='# playbook',
        playbook=playbook.json()['url'],
        is_playbook=True
    )
)

task_file = post(
    '/api/v1/files/',
    dict(
        playbook=playbook.json()['url'],
        path='/tmp/task.yml',
        # TODO: Fix this somehow
        content='# task',
        is_playbook=True
    )
)

task = post(
    '/api/v1/tasks/',
    dict(
        playbook=playbook.json()['url'],
        play=play.json()['url'],
        file=task_file.json()['url'],
        name='Task name',
        action='action',
        lineno=1,
        tags=json.dumps(['one', 'two']),
        handler=False,
        started='2016-05-06T17:20:25.749489-04:00'
    )
)
