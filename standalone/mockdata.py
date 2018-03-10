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

# Creates fake data in the database, bypassing the API.
import django
import hashlib
import os
import sys
from django.core import serializers

parent_directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parent_directory)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ara.settings')
django.setup()

from api import models

playbook, _ = models.Playbook.objects.get_or_create(
    started='2016-05-06T17:20:25.749489-04:00',
    path='/tmp/test.yml',
    ansible_version='2.3.4',
    completed=False,
)
print(serializers.serialize('json',
                            models.Playbook.objects.all(),
                            indent=2))

play, _ = models.Play.objects.get_or_create(
    started='2016-05-06T17:20:25.749489-04:00',
    name='Test play',
    playbook=playbook,
)
print(serializers.serialize('json',
                            models.Play.objects.all(),
                            indent=2))

content = 'foo'.encode('utf8')
filecontent, _ = models.FileContent.objects.get_or_create(
    contents=content,
    sha1=hashlib.sha1(content).hexdigest()
)
print(serializers.serialize('json',
                            models.FileContent.objects.all(),
                            indent=2))

file, _ = models.File.objects.get_or_create(
    playbook=playbook,
    content=filecontent,
    path='/tmp/anothertest.yml'
)
print(serializers.serialize('json',
                            models.File.objects.all(),
                            indent=2))
