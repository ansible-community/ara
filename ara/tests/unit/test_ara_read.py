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

from collections import defaultdict
import random

import ara.models as m
import ara.plugins.callbacks.log_ara as l
import ara.plugins.actions.ara_record as ara_record
import ara.plugins.actions.ara_read as ara_read

from ara.tests.unit.common import TestAra

from mock import Mock
from mock import MagicMock


class Playbook(object):
    def __init__(self, path):
        self._file_name = path
        self.path = path
        self.options = {'fake': 'yes'}


class Play(object):
    def __init__(self, name):
        self.name = name


class Task(object):
    def __init__(self, name, path, lineno=1, action='fakeaction'):
        self.name = name
        self.action = action
        self.path = '%s:%d' % (path, lineno)
        self._attributes = {'tags': []}

    def get_path(self):
        """ Ansible Module/Callback specific method """
        return self.path

    def get_name(self):
        """ Ansible Module/Callback specific method """
        return self.name


class TaskResult(object):
    def __init__(self, task, host, status, changed=False):
        assert status in ['ok', 'failed', 'skipped', 'unreachable']

        self.task = task
        self.status = status
        self._host = MagicMock()
        self._host.get_name.return_value = host

        self._result = {
            'changed': changed,
            'failed': status == 'failed',
            'skipped': status == 'skipped',
            'unreachable': status == 'unreachable',
        }


class Stats(object):
    def __init__(self, processed):
        self.processed = processed

    def summarize(self, name):
        return {
            'failures': self.processed[name]['failed'],
            'ok': self.processed[name]['ok'],
            'changed': self.processed[name]['changed'],
            'skipped': self.processed[name]['skipped'],
            'unreachable': self.processed[name]['unreachable'],
        }


class TestRead(TestAra):
    """ Tests for the Ansible ara_read module """
    def setUp(self):
        super(TestRead, self).setUp()

        self.cb = l.CallbackModule()
        self.tag = '%04d' % random.randint(0, 9999)
        self.ansible_run()

    def tearDown(self):
        super(TestRead, self).tearDown()

    def ansible_run(self):
        '''Simulates an ansible run by creating stub versions of the
        information that Ansible passes to the callback, and then
        calling the various callback methods.'''

        self.playbook = self._test_playbook()
        self.play = self._test_play()
        self.task = self._test_task(self.playbook)
        self.results = [
            self._test_result(self.task, 'host1', 'ok', changed=True),
        ]

        self.stats = self._test_stats()

        # Record a k/v pair to test with
        self.play_context = Mock()
        self.play_context.check_mode = False
        self.connection = Mock()

        self.task = MagicMock(Task)
        self.task.async_ = 0
        self.task.async_val = False
        self.task.args = {
            'key': 'test-key',
            'value': 'test-value',
            'type': 'text'
        }

        action = ara_record.ActionModule(self.task, self.connection,
                                         self.play_context, loader=None,
                                         templar=None, shared_loader_obj=None)
        action.run()

    def _test_stats(self):
        stats = Stats({
            'host1': defaultdict(int, ok=1, changed=1),
            'host2': defaultdict(int, failed=1),
        })

        self.cb.v2_playbook_on_stats(stats)
        return stats

    def _test_result(self, task, host, status='ok', changed=False):
        result = TaskResult(task, host, status, changed)
        func = getattr(self.cb, 'v2_runner_on_%s' % status)
        func(result)
        return result

    def _test_playbook(self):
        path = '/test-playbook-%s.yml' % self.tag
        playbook = Playbook(path)
        self.cb.v2_playbook_on_start(playbook)
        return playbook

    def _test_play(self):
        name = 'test-play-%s' % self.tag
        play = Play(name)
        self.cb.v2_playbook_on_play_start(play)
        return play

    def _test_task(self, playbook):
        name = 'test-task-%s' % self.tag
        task = Task(name, playbook.path)
        task.async_val = False
        self.cb.v2_playbook_on_task_start(task, False)
        return task

    def test_read_record_with_playbook(self):
        """
        Read an existing record with ara_read for a specified playbook
        """
        r_playbook = m.Playbook.query.first()
        self.assertIsNotNone(r_playbook)

        task = MagicMock(Task)
        task.async_ = 0
        task.async_val = False
        task.args = {
            'playbook': r_playbook.id,
            'key': 'test-key',
        }

        action = ara_read.ActionModule(task, self.connection,
                                       self.play_context, loader=None,
                                       templar=None, shared_loader_obj=None)
        data = action.run()

        r_data = m.Data.query.filter_by(playbook_id=r_playbook.id,
                                        key='test-key').one()
        self.assertIsNotNone(r_data)
        self.assertEqual(r_data.playbook_id, r_playbook.id)
        self.assertEqual(r_data.key, 'test-key')
        self.assertEqual(r_data.value, 'test-value')
        self.assertEqual(r_data.type, 'text')

        self.assertEqual(data['playbook_id'], r_data.playbook_id)
        self.assertEqual(data['key'], r_data.key)
        self.assertEqual(data['value'], r_data.value)
        self.assertEqual(data['type'], r_data.type)

    def test_read_record(self):
        """
        Read an existing record with ara_read
        """
        task = MagicMock(Task)
        task.async_ = 0
        task.async_val = False
        task.args = {
            'key': 'test-key',
        }

        action = ara_read.ActionModule(task, self.connection,
                                       self.play_context, loader=None,
                                       templar=None, shared_loader_obj=None)
        data = action.run()

        r_playbook = m.Playbook.query.first()
        self.assertIsNotNone(r_playbook)

        r_data = m.Data.query.filter_by(playbook_id=r_playbook.id,
                                        key='test-key').one()
        self.assertIsNotNone(r_data)
        self.assertEqual(r_data.playbook_id, r_playbook.id)
        self.assertEqual(r_data.key, 'test-key')
        self.assertEqual(r_data.value, 'test-value')
        self.assertEqual(r_data.type, 'text')

        self.assertEqual(data['playbook_id'], r_data.playbook_id)
        self.assertEqual(data['key'], r_data.key)
        self.assertEqual(data['value'], r_data.value)
        self.assertEqual(data['type'], r_data.type)

    def test_read_record_with_no_key(self):
        """
        Read an existing record that does not exist with ara_read
        """
        task = MagicMock(Task)
        task.async_ = 0
        task.async_val = False
        task.args = {
            'key': 'key',
        }

        action = ara_read.ActionModule(task, self.connection,
                                       self.play_context, loader=None,
                                       templar=None, shared_loader_obj=None)
        data = action.run()

        r_playbook = m.Playbook.query.first()
        self.assertIsNotNone(r_playbook)

        # There is no exception raised in the action module, we instead
        # properly return a failure status to Ansible.
        # If there is a failure, no data will be returned so we can catch this.
        with self.assertRaises(Exception):
            m.Data.query.filter_by(playbook_id=r_playbook.id, key='key').one()

        self.assertEqual(data['failed'], True)
        self.assertEqual(data['playbook_id'], None)
        self.assertEqual(data['key'], None)
        self.assertEqual(data['value'], None)
