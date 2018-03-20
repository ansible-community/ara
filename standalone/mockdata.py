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
import json
import os
import sys

parent_directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parent_directory)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ara.settings')
django.setup()

from django.test import Client


def post(endpoint, data):
    client = Client()
    print("Posting to %s..." % endpoint)
    obj = client.post(endpoint,
                      json.dumps(data),
                      content_type="application/json")
    print("HTTP %s" % obj.status_code)
    print("Got: %s" % json.dumps(obj.json(), indent=2))
    print("#" * 40)
    return obj.json()


playbook = post(
    '/api/v1/playbooks/',
    {
        'started': '2016-05-06T17:20:25.749489-04:00',
        'ansible_version': '2.3.4',
        'completed': False,
        'parameters': {'foo': 'bar'}
    }
)

playbook_with_files = post(
    '/api/v1/playbooks/',
    {
        'started': '2016-05-06T17:20:25.749489-04:00',
        'ansible_version': '2.3.4',
        'completed': False,
        'parameters': {'foo': 'bar'},
        'files': [
            {'path': '/tmp/1/playbook.yml', 'content': '# playbook'},
            {'path': '/tmp/2/playbook.yml', 'content': '# playbook'}
        ],
    }
)

play = post(
    '/api/v1/plays/',
    {
        'started': '2016-05-06T17:20:25.749489-04:00',
        'name': 'Test play',
        'playbook': playbook['id']
    }
)
