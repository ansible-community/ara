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

import ara.models as m
import random

from ansible import __version__ as ansible_version
from mock import MagicMock
from oslo_serialization import jsonutils

FAKE_PLAYBOOK_CONTENT = """---
- name: ARA unit tests
  hosts: localhost
  gather_facts: yes
  tasks:
    - debug:
        msg: 'Unit tests, yay!'
"""

FAKE_TASK_CONTENT = """---
- debug:
    msg: 'task'
"""

DEFAULT_CONTENT = """---
# YAML should be here"""


class Data(object):
    def __init__(self, playbook=None, key='test key', value='test value'):
        if playbook is None:
            playbook = Playbook().model
        self.playbook = playbook
        self.key = key
        self.value = value

    @property
    def model(self):
        return m.Data(playbook=self.playbook,
                      key=self.key,
                      value=self.value)


class File(object):
    def __init__(self, is_playbook=False, path='main.yml', playbook=None):
        self.is_playbook = is_playbook
        self.path = path
        if playbook is None:
            playbook = Playbook(path=self.path).model
        self.playbook = playbook

    @property
    def model(self):
        return m.File(is_playbook=self.is_playbook,
                      path=self.path,
                      playbook=self.playbook)


class FileContent(object):
    def __init__(self, content=DEFAULT_CONTENT):
        self.content = content

    @property
    def model(self):
        sha1 = m.content_sha1(self.content)
        content = m.FileContent.query.get(sha1)

        if content is None:
            return m.FileContent(content=self.content)
        else:
            return content


class Host(object):
    def __init__(self, name=None, playbook=None):
        if name is None:
            name = 'host-%04d' % random.randint(0, 9999)
        self.name = name
        if playbook is None:
            playbook = Playbook().model
        self.playbook = playbook

    def get_name(self):
        """ Callback specific method """
        return self.name

    @property
    def model(self):
        return m.Host(name=self.name,
                      playbook=self.playbook)


class HostFacts(object):
    def __init__(self, host=None, values=None):
        if host is None:
            host = Host().model
        self.host = host
        if values is None:
            values = '{"fact": "value"}'
        self.values = values

    @property
    def model(self):
        return m.HostFacts(host=self.host,
                           values=self.values)


class Playbook(object):
    def __init__(self, complete=True, path='playbook.yml',
                 options={'fake': 'yes'}):
        self.ansible_version = ansible_version
        self.complete = complete
        self.options = options
        self.path = path

        # Callback specific parameter
        self._file_name = path

    @property
    def model(self):
        return m.Playbook(ansible_version=ansible_version,
                          complete=self.complete,
                          options=self.options,
                          path=self.path)


class Play(object):
    def __init__(self, name='ARA unit tests', playbook=None):
        self.name = name
        if playbook is None:
            playbook = Playbook().model
        self.playbook = playbook

    @property
    def model(self):
        return m.Play(name=self.name,
                      playbook=self.playbook)


class Task(object):
    def __init__(self, action='fake_action', lineno=1, name='Fake action',
                 playbook=None, play=None, file=None, file_id=None, path=None,
                 tags=None):
        self.action = action
        if tags is None:
            tags = []
        self.tags = tags
        self.lineno = lineno
        self.name = name
        if playbook is None:
            playbook = Playbook().model
        self.playbook = playbook
        if play is None:
            play = Play(playbook=self.playbook).model
        self.play = play
        self.file = file
        self.file_id = file_id

        # Callback specific parameter
        if path is None:
            path = playbook.path
        self.path = '%s:%d' % (path, self.lineno)
        self._attributes = {'tags': self.tags}

    def get_path(self):
        """ Callback specific method """
        return self.path

    def get_name(self):
        """ Callback specific method """
        return self.name

    @property
    def model(self):
        return m.Task(action=self.action,
                      tags=jsonutils.dumps(self.tags),
                      lineno=self.lineno,
                      name=self.name,
                      playbook=self.playbook,
                      play=self.play,
                      file=self.file,
                      file_id=self.file_id)


class TaskResult(object):
    def __init__(self, task=None, host=None, status='ok', ignore_errors=False,
                 changed=True, failed=False, skipped=False, unreachable=False,
                 result='Task result <here>'):
        assert status in ['ok', 'failed', 'skipped', 'unreachable']

        if task is None:
            task = Task().model
        self.task = task
        if host is None:
            host = Host(playbook=self.task.playbook)
        self.host = host
        self.status = status
        self.ignore_errors = ignore_errors
        self.changed = changed
        self.failed = failed
        self.skipped = skipped
        self.unreachable = unreachable
        self.result = result

        # Callback specific parameters
        self._host = MagicMock()
        self._host.get_name.return_value = host
        self._result = {
            'changed': self.changed,
            'failed': self.failed,
            'skipped': self.skipped,
            'unreachable': self.unreachable
        }

    @property
    def model(self):
        return m.TaskResult(task=self.task,
                            host=self.host,
                            status=self.status,
                            ignore_errors=self.ignore_errors,
                            changed=self.changed,
                            failed=self.failed,
                            skipped=self.skipped,
                            unreachable=self.unreachable,
                            result=self.result)


class Stats(object):
    def __init__(self, playbook=None, host=None, changed=1, failed=0, ok=1,
                 skipped=1, unreachable=0, processed=None):
        if playbook is None:
            playbook = Playbook().model
        self.playbook = playbook
        if host is None:
            host = Host(playbook=self.playbook).model
        self.host = host
        self.changed = changed
        self.failed = failed
        self.ok = ok
        self.skipped = skipped
        self.unreachable = unreachable

        # Callback specific parameter
        if processed is not None:
            self.processed = processed

    def summarize(self, name):
        """ Callback specific method """
        return {
            'failures': self.processed[name]['failed'],
            'ok': self.processed[name]['ok'],
            'changed': self.processed[name]['changed'],
            'skipped': self.processed[name]['skipped'],
            'unreachable': self.processed[name]['unreachable'],
        }

    @property
    def model(self):
        return m.Stats(playbook=self.playbook,
                       host=self.host,
                       changed=self.changed,
                       failed=self.failed,
                       ok=self.ok,
                       skipped=self.skipped,
                       unreachable=self.unreachable)
