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

import ara.db.models as m
import ara.plugins.callbacks.log_ara as log_ara
import ara.plugins.actions.ara_record as ara_record
import random

from ansible import __version__ as ansible_version
from mock import Mock
from mock import MagicMock
from oslo_serialization import jsonutils

FAKE_PLAYBOOK_CONTENT = """---
- name: ARA unit tests
  hosts: all
  tasks:
    - name: Retrieve host facts
      setup:
      when: gather_facts

    - name: Record something
      ara_record:
        playbook_id: 'unit test magic'
        key: 'test key'
        value: 'test value'
        type: 'text'

    - name: Skip something
      debug:
        msg: This is skipped
      when: ara != awesome

    - name: Fail something
      fail:
"""

FAKE_TASK_CONTENT = """---
- debug:
    msg: 'task'
"""

DEFAULT_CONTENT = """---
# YAML should be here"""


class AnsiblePlaybook(object):
    """ Simple representation of a fake Ansible playbook object """
    def __init__(self, path='/playbook.yml', content=FAKE_PLAYBOOK_CONTENT):
        self._file_name = path
        self._loader = MagicMock()
        self._loader._FILE_CACHE.return_value = {
            path: content
        }
        self._options = MagicMock()
        self._options.inventory = '/etc/ansible/hosts'


class AnsiblePlay(object):
    """ Simple representation of a fake Ansible play object """
    def __init__(self, path='/playbook.yml', content=FAKE_PLAYBOOK_CONTENT,
                 name='ARA unit tests', hosts=None):
        self._loader = MagicMock()
        self._loader._FILE_CACHE.return_value = {
            path: content
        }
        self.name = name
        self._variable_manager = MagicMock()
        self._variable_manager._inventory._restriction = hosts


class AnsibleTask(object):
    """ Simple representation of a fake Ansible task object """
    def __init__(self, name='ARA test task', action='debug',
                 path='/task.yml:1', args=None, tags=['tag']):
        self.name = name
        self.action = action
        self.path = path
        self.args = args
        self.async = 0

        self._attributes = {
            'tags': tags
        }

    def get_path(self):
        return self.path

    def get_name(self):
        return self.name


class AnsibleResult(object):
    """ Simple representation of a fake Ansible result object """
    def __init__(self, host=None, result=None):
        if host is None:
            host = AnsibleHost()
        self._host = host

        if result is None:
            result = dict(
                msg='test result',
                changed=False,
                failed=False,
                skipped=False,
                unreachable=False,
                ignore_errors=False
            )
        self._result = result


class AnsibleHost(object):
    """ Simple representation of a fake Ansible host object """
    def __init__(self, name='host1'):
        self.name = name

        # These are just for convenience for tracking fake stats
        self.changed = 0
        self.failed = 0
        self.ok = 0
        self.skipped = 0
        self.unreachable = 0

    def get_name(self):
        return self.name


class AnsibleStats(object):
    """ Simple representation of a fake Ansible stats object """
    def __init__(self, hosts=None):
        if hosts is None:
            hosts = [AnsibleHost()]

        self.processed = {
            host.name: dict(
                changed=host.changed,
                failed=host.failed,
                ok=host.ok,
                skipped=host.skipped,
                unreachable=host.unreachable
            )
            for host in hosts
        }

    def summarize(self, name):
        return {
            'failures': self.processed[name]['failed'],
            'ok': self.processed[name]['ok'],
            'changed': self.processed[name]['changed'],
            'skipped': self.processed[name]['skipped'],
            'unreachable': self.processed[name]['unreachable'],
        }


class FakeRun(object):
    """ Simulates an ansible run by creating stub versions of the
    information that Ansible passes to the callback, and then
    calling the various callback methods. """
    def __init__(self, completed=True, host_facts=True, record_task=True,
                 record_data=None):
        self.cb = log_ara.CallbackModule()

        self.playbook = AnsiblePlaybook()
        self.playbook = self.cb.v2_playbook_on_start(self.playbook)

        self.host_one = AnsibleHost(name='host_one')
        self.host_two = AnsibleHost(name='host_two')
        self.play = AnsiblePlay(hosts=[
            self.host_one.name,
            self.host_two.name
        ])
        self.play = self.cb.v2_playbook_on_play_start(self.play)

        # Simulate an 'ok' task
        if host_facts:
            self.t_ok = AnsibleTask(
                name='Retrieve host facts',
                action='setup',
                path='%s:%s' % (self.playbook['path'], 4),
                args={}
            )
            self.t_ok = self.cb.v2_playbook_on_task_start(self.t_ok, False)

            result = {
                'ansible_facts': {
                    'cpu': '9001'
                }
            }
            self.r_ok = [
                self._task_result('ok', host=self.host_one, result=result),
                self._task_result('ok', host=self.host_two, result=result)
            ]

        if record_task:
            # Simulate a 'changed' task
            self.play_context = Mock()
            self.play_context.check_mode = False
            self.connection = Mock()

            if record_data is None:
                record_data = {
                    'playbook': self.playbook['id'],
                    'key': 'test-text',
                    'value': 'test-with-playbook',
                    'type': 'text'
                }
            else:
                record_data['playbook'] = self.playbook['id']

            self.t_changed = AnsibleTask(
                name='Record something',
                action='ara_record',
                path='%s:%s' % (self.playbook['path'], 8),
                args=record_data
            )

            result = dict(
                changed=True,
                **record_data
            )
            self.r_changed = [
                self._task_result('ok', host=self.host_one, result=result),
                self._task_result('ok', host=self.host_two, result=result)
            ]
            # Record the actual data with the module
            action = ara_record.ActionModule(self.t_changed, self.connection,
                                             self.play_context, loader=None,
                                             templar=None,
                                             shared_loader_obj=None)
            action.run()

        # Simulate a 'skipped' task
        self.t_skipped = AnsibleTask(
            name='Skipped something',
            action='debug',
            path='%s:%s' % (self.playbook['path'], 15),
            args={'msg': 'This is skipped'}
        )
        self.t_skipped = self.cb.v2_playbook_on_task_start(self.t_skipped,
                                                           False)

        result = {
            'skipped': True
        }
        self.r_skipped = [
            self._task_result('skipped', host=self.host_one, result=result),
            self._task_result('skipped', host=self.host_two, result=result)
        ]

        # Simulate a 'failed' task
        self.t_failed = AnsibleTask(
            name='Failed something',
            action='fail',
            path='%s:%s' % (self.playbook['path'], 20),
            args={}
        )
        self.t_failed = self.cb.v2_playbook_on_task_start(self.t_failed,
                                                          False)

        result = {
            'failed': True
        }
        self.r_failed = [
            self._task_result('failed', host=self.host_one, result=result)
            # host_two is unreachable, see next task
        ]

        # Simulate an 'unreachable' task
        self.t_unreach = AnsibleTask(
            name='Failed something',
            action='fail',
            path='%s:%s' % (self.playbook['path'], 20),
            args={}
        )
        self.t_unreach = self.cb.v2_playbook_on_task_start(self.t_unreach,
                                                           False)

        result = {
            'unreachable': True
        }
        self.r_unreach = [
            self._task_result('unreachable', host=self.host_two, result=result)
        ]

        if completed:
            self.stats = AnsibleStats(hosts=[
                self.host_one,
                self.host_two
            ])
            self.cb.v2_playbook_on_stats(self.stats)

    def _task_result(self, status, host, result):
        """ Creates a result and runs the appropriate callback hook """
        res = AnsibleResult(host=host, result=result)
        hook = getattr(self.cb, 'v2_runner_on_%s' % status)
        hook(res)

        # Increment stats
        real_host = getattr(self, host.name)
        setattr(real_host, status, getattr(real_host, status) + 1)
        return res


# TODO: Get rid of those model fakes, use the "real" Ansible ones.
class Record(object):
    def __init__(self, playbook=None, key='test key', value='test value'):
        if playbook is None:
            playbook = Playbook().model
        self.playbook = playbook
        self.key = key
        self.value = value

    @property
    def model(self):
        return m.Record(playbook=self.playbook,
                        key=self.key,
                        value=self.value)


class File(object):
    def __init__(self, is_playbook=False, path='main.yml', playbook=None,
                 content=None):
        self.is_playbook = is_playbook
        self.path = path
        if playbook is None:
            playbook = Playbook(path=self.path).model
        self.playbook = playbook
        if content is None:
            content = FileContent().model
        self.content = content

    @property
    def model(self):
        return m.File(is_playbook=self.is_playbook,
                      path=self.path,
                      playbook=self.playbook,
                      content=self.content)


class FileContent(object):
    def __init__(self, content=FAKE_PLAYBOOK_CONTENT):
        self.content = content

    @property
    def model(self):
        sha1 = m.content_sha1(self.content)

        try:
            content = m.FileContent.query.filter_by(sha1=sha1).one()
            return content
        except m.NoResultFound:
            return m.FileContent(content=self.content)


class Host(object):
    def __init__(self, name=None, playbook=None, facts=None, changed=0,
                 failed=0, ok=0, skipped=0, unreachable=0):
        if name is None:
            name = 'host-%04d' % random.randint(0, 9999)
        self.name = name
        if playbook is None:
            playbook = Playbook().model
        self.playbook = playbook
        self.facts = facts

        self.changed = changed
        self.failed = failed
        self.ok = ok
        self.skipped = skipped
        self.unreachable = unreachable

    def get_name(self):
        """ Callback specific method """
        return self.name

    @property
    def model(self):
        return m.Host(name=self.name,
                      playbook=self.playbook,
                      facts=self.facts,
                      changed=self.changed,
                      failed=self.failed,
                      ok=self.ok,
                      skipped=self.skipped,
                      unreachable=self.unreachable)


class Playbook(object):
    def __init__(self, completed=True, path='playbook.yml',
                 parameters={'fake': 'yes'}):

        self.ansible_version = ansible_version
        self.completed = completed
        self.parameters = parameters
        self.path = path

        # Callback specific parameters
        self._loader = MagicMock()
        self._loader._FILE_CACHE.return_value = {
            self.path: FAKE_PLAYBOOK_CONTENT
        }
        self._file_name = path

    @property
    def model(self):
        return m.Playbook(ansible_version=ansible_version,
                          completed=self.completed,
                          parameters=self.parameters,
                          path=self.path)


class Play(object):
    def __init__(self, name='ARA unit tests', playbook=None):
        self.name = name
        if playbook is None:
            playbook = Playbook().model
        self.playbook = playbook

        # Callback specific parameters
        hosts = [host.name for host in self.playbook.hosts.all()]
        self._variable_manager = MagicMock()
        self._variable_manager._inventory._restriction.return_value = hosts
        self._loader = MagicMock()
        self._loader._FILE_CACHE.return_value = {
            self.playbook.path: FAKE_PLAYBOOK_CONTENT
        }

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


class Result(object):
    def __init__(self, playbook=None, play=None, task=None, host=None,
                 status='ok', ignore_errors=False, changed=True, failed=False,
                 skipped=False, unreachable=False,
                 result='Task result <here>'):
        assert status in ['ok', 'failed', 'skipped', 'unreachable']

        if playbook is None:
            playbook = Playbook().model
        self.playbook = playbook
        if play is None:
            play = Play().model
        self.play = play
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
        return m.Result(playbook=self.playbook,
                        play=self.play,
                        task=self.task,
                        host=self.host,
                        status=self.status,
                        ignore_errors=self.ignore_errors,
                        changed=self.changed,
                        failed=self.failed,
                        skipped=self.skipped,
                        unreachable=self.unreachable,
                        result=self.result)
