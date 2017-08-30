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

from ara.api.plays import PlayApi
from ara.api.playbooks import PlaybookApi
from ara.api.tasks import TaskApi
import ara.plugins.callbacks.log_ara as log_ara
import ara.plugins.actions.ara_record as ara_record

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
        self._loader._FILE_CACHE = {
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

            record = AnsibleTask(
                name='Record something',
                action='ara_record',
                path='%s:%s' % (self.playbook['path'], 8),
                args=record_data
            )
            self.t_changed = self.cb.v2_playbook_on_task_start(record, False)

            result = dict(
                changed=True,
                **record_data
            )
            self.r_changed = [
                self._task_result('ok', host=self.host_one, result=result),
                self._task_result('ok', host=self.host_two, result=result)
            ]
            # Record the actual data with the module
            action = ara_record.ActionModule(record, self.connection,
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

        # Playbooks, plays and tasks can "lag" behind because they are first
        # created and then "children" are created. Refresh their reference at
        # the end so we have a complete set with the children.
        updated = PlaybookApi().get(id=self.playbook['id'])
        self.playbook = jsonutils.loads(updated.data)

        updated = PlayApi().get(id=self.play['id'])
        self.play = jsonutils.loads(updated.data)

        for task in ['t_ok', 't_changed', 't_failed', 't_skipped',
                     't_unreach']:
            if getattr(self, task, None):
                updated = TaskApi().get(id=getattr(self, task)['id'])
                setattr(self, task, jsonutils.loads(updated.data))

    def _task_result(self, status, host, result):
        """ Creates a result and runs the appropriate callback hook """
        res = AnsibleResult(host=host, result=result)
        hook = getattr(self.cb, 'v2_runner_on_%s' % status)
        hook(res)

        # Increment stats based on the result
        real_host = getattr(self, host.name)
        setattr(real_host, status, getattr(real_host, status) + 1)
        if 'changed' in result and result['changed']:
            setattr(real_host, 'changed', getattr(real_host, 'changed') + 1)
        return res
