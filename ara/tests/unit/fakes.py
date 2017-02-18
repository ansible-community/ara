#   Copyright 2017 Red Hat, Inc. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

import hashlib
import random

import ara.models as m

from mock import Mock
from ansible import __version__ as ansible_version

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
        sha1 = hashlib.sha1(self.content).hexdigest()
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
    def __init__(self, complete=True, path='playbook.yml'):
        self.ansible_version = ansible_version
        self.complete = complete
        self.path = path

        # Callback specific parameter
        self._file_name = path

    @property
    def model(self):
        return m.Playbook(ansible_version=ansible_version,
                          complete=self.complete,
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
                 playbook=None, play=None, file=None, file_id=None, path=None):
        self.action = action
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

    def get_path(self):
        """ Callback specific method """
        return self.path

    @property
    def model(self):
        return m.Task(action=self.action,
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
        self.skipped = skipped,
        self.unreachable = unreachable
        self.result = result

        # Callback specific parameters
        self._host = Mock()
        self._host.name = self.host
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
