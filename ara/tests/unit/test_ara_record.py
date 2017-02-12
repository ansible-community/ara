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

from collections import defaultdict
import random

import ara.models as m
import ara.plugins.callbacks.log_ara as l
import ara.plugins.actions.ara_record as ara_record

from ara.tests.unit.common import TestAra

from mock import Mock, MagicMock


class Playbook(object):
    def __init__(self, path):
        self._file_name = path
        self.path = path


class Play(object):
    def __init__(self, name):
        self.name = name


class Task(object):
    def __init__(self, name, path, lineno=1, action='fakeaction'):
        self.name = name
        self.action = action
        self.path = '%s:%d' % (path, lineno)

    def get_path(self):
        return self.path


class TaskResult(object):
    def __init__(self, task, host, status, changed=False):
        assert status in ['ok', 'failed', 'skipped', 'unreachable']

        self.task = task
        self.status = status
        self._host = Mock()
        self._host.name = host
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


class TestRecord(TestAra):
    '''Tests for the Ansible ara_record module'''
    def setUp(self):
        super(TestRecord, self).setUp()

        self.cb = l.CallbackModule()
        self.tag = '%04d' % random.randint(0, 9999)

        self.ansible_run()

        self.play_context = Mock()
        self.play_context.check_mode = False
        self.connection = Mock()

    def tearDown(self):
        super(TestRecord, self).tearDown()

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
        self.cb.v2_playbook_on_task_start(task, False)
        return task

    def test_create_text_record(self):
        """
        Create a new record with ara_record.
        """
        task = MagicMock(Task)
        task.async = MagicMock()
        task.args = {
            'key': 'test-text',
            'value': 'test-value',
            'type': 'text'
        }

        action = ara_record.ActionModule(task, self.connection,
                                         self.play_context, loader=None,
                                         templar=None, shared_loader_obj=None)
        action.run()

        r_playbook = m.Playbook.query.first()
        self.assertIsNotNone(r_playbook)

        r_data = m.Data.query.filter_by(playbook_id=r_playbook.id,
                                        key='test-text').one()
        self.assertIsNotNone(r_data)
        self.assertEqual(r_data.playbook_id, r_playbook.id)
        self.assertEqual(r_data.key, 'test-text')
        self.assertEqual(r_data.value, 'test-value')
        self.assertEqual(r_data.type, 'text')

    def test_create_url_record(self):
        """
        Create a new record with ara_record.
        """
        task = MagicMock(Task)
        task.async = MagicMock()
        task.args = {
            'key': 'test-url',
            'value': 'http://url',
            'type': 'url'
        }

        action = ara_record.ActionModule(task, self.connection,
                                         self.play_context, loader=None,
                                         templar=None, shared_loader_obj=None)
        action.run()

        r_playbook = m.Playbook.query.first()
        self.assertIsNotNone(r_playbook)

        r_data = m.Data.query.filter_by(playbook_id=r_playbook.id,
                                        key='test-url').one()
        self.assertIsNotNone(r_data)
        self.assertEqual(r_data.playbook_id, r_playbook.id)
        self.assertEqual(r_data.key, 'test-url')
        self.assertEqual(r_data.value, 'http://url')
        self.assertEqual(r_data.type, 'url')

    def test_create_json_record(self):
        """
        Create a new record with ara_record.
        """
        task = MagicMock(Task)
        task.async = MagicMock()
        task.args = {
            'key': 'test-json',
            'value': '{"foo": "bar"}',
            'type': 'json'
        }

        action = ara_record.ActionModule(task, self.connection,
                                         self.play_context, loader=None,
                                         templar=None, shared_loader_obj=None)
        action.run()

        r_playbook = m.Playbook.query.first()
        self.assertIsNotNone(r_playbook)

        r_data = m.Data.query.filter_by(playbook_id=r_playbook.id,
                                        key='test-json').one()
        self.assertIsNotNone(r_data)
        self.assertEqual(r_data.playbook_id, r_playbook.id)
        self.assertEqual(r_data.key, 'test-json')
        self.assertEqual(r_data.value, '{"foo": "bar"}')
        self.assertEqual(r_data.type, 'json')

    def test_create_list_record(self):
        """
        Create a new record with ara_record.
        """
        task = MagicMock(Task)
        task.async = MagicMock()
        task.args = {
            'key': 'test-list',
            'value': ['foo', 'bar'],
            'type': 'list'
        }

        action = ara_record.ActionModule(task, self.connection,
                                         self.play_context, loader=None,
                                         templar=None, shared_loader_obj=None)
        action.run()

        r_playbook = m.Playbook.query.first()
        self.assertIsNotNone(r_playbook)

        r_data = m.Data.query.filter_by(playbook_id=r_playbook.id,
                                        key='test-list').one()
        self.assertIsNotNone(r_data)
        self.assertEqual(r_data.playbook_id, r_playbook.id)
        self.assertEqual(r_data.key, 'test-list')
        self.assertEqual(r_data.value, ['foo', 'bar'])
        self.assertEqual(r_data.type, 'list')

    def test_create_dict_record(self):
        """
        Create a new record with ara_record.
        """
        task = MagicMock(Task)
        task.async = MagicMock()
        task.args = {
            'key': 'test-dict',
            'value': {'foo': 'bar'},
            'type': 'dict'
        }

        action = ara_record.ActionModule(task, self.connection,
                                         self.play_context, loader=None,
                                         templar=None, shared_loader_obj=None)
        action.run()

        r_playbook = m.Playbook.query.first()
        self.assertIsNotNone(r_playbook)

        r_data = m.Data.query.filter_by(playbook_id=r_playbook.id,
                                        key='test-dict').one()
        self.assertIsNotNone(r_data)
        self.assertEqual(r_data.playbook_id, r_playbook.id)
        self.assertEqual(r_data.key, 'test-dict')
        self.assertEqual(r_data.value, {'foo': 'bar'})
        self.assertEqual(r_data.type, 'dict')

    def test_create_record_with_no_type(self):
        """
        Create a new record with ara_record with no type specified.
        """
        task = MagicMock(Task)
        task.async = MagicMock()
        task.args = {
            'key': 'test-notype',
            'value': 'test-value'
        }

        action = ara_record.ActionModule(task, self.connection,
                                         self.play_context, loader=None,
                                         templar=None, shared_loader_obj=None)
        action.run()

        r_playbook = m.Playbook.query.first()
        self.assertIsNotNone(r_playbook)

        r_data = m.Data.query.filter_by(playbook_id=r_playbook.id,
                                        key='test-notype').one()
        self.assertIsNotNone(r_data)
        self.assertEqual(r_data.playbook_id, r_playbook.id)
        self.assertEqual(r_data.key, 'test-notype')
        self.assertEqual(r_data.value, 'test-value')
        self.assertEqual(r_data.type, 'text')

    def test_create_record_as_wrong_type(self):
        """
        Create a new record with ara_record.
        """
        task = MagicMock(Task)
        task.async = MagicMock()
        task.args = {
            'key': 'test-wrongtype',
            'value': ['foo', 'bar'],
            'type': 'text'
        }

        action = ara_record.ActionModule(task, self.connection,
                                         self.play_context, loader=None,
                                         templar=None, shared_loader_obj=None)
        action.run()

        r_playbook = m.Playbook.query.first()
        self.assertIsNotNone(r_playbook)

        r_data = m.Data.query.filter_by(playbook_id=r_playbook.id,
                                        key='test-wrongtype').one()
        self.assertIsNotNone(r_data)
        self.assertEqual(r_data.playbook_id, r_playbook.id)
        self.assertEqual(r_data.key, 'test-wrongtype')
        self.assertEqual(r_data.value, ['foo', 'bar'])
        self.assertEqual(r_data.type, 'text')

    def test_update_record(self):
        """
        Update an existing record by running ara_record a second time on the
        same key.
        """
        task = MagicMock(Task)
        task.async = MagicMock()
        task.args = {
            'key': 'test-update',
            'value': 'test-value',
            'type': 'text'
        }

        action = ara_record.ActionModule(task, self.connection,
                                         self.play_context, loader=None,
                                         templar=None, shared_loader_obj=None)
        action.run()

        r_playbook = m.Playbook.query.first()
        self.assertIsNotNone(r_playbook)

        r_data = m.Data.query.filter_by(playbook_id=r_playbook.id,
                                        key='test-update').one()
        self.assertIsNotNone(r_data)
        self.assertEqual(r_data.playbook_id, r_playbook.id)
        self.assertEqual(r_data.key, 'test-update')
        self.assertEqual(r_data.value, 'test-value')
        self.assertEqual(r_data.type, 'text')

        task.args = {
            'key': 'test-update',
            'value': 'http://another-value',
            'type': 'url'
        }
        action = ara_record.ActionModule(task, self.connection,
                                         self.play_context, loader=None,
                                         templar=None, shared_loader_obj=None)
        action.run()

        r_data = m.Data.query.filter_by(playbook_id=r_playbook.id,
                                        key='test-update').one()

        self.assertEqual(r_data.value, 'http://another-value')
        self.assertEqual(r_data.type, 'url')

    def test_record_with_no_key(self):
        """
        Trying to use ara_record with no key parameter should properly fail
        """
        task = MagicMock(Task)
        task.async = MagicMock()
        task.args = {
            'value': 'test-value'
        }

        action = ara_record.ActionModule(task, self.connection,
                                         self.play_context, loader=None,
                                         templar=None, shared_loader_obj=None)
        action.run()

        r_playbook = m.Playbook.query.first()
        self.assertIsNotNone(r_playbook)

        # There is no exception raised in the action module, we instead
        # properly return a failure status to Ansible.
        # If there is a failure, no data will be recorded so we can catch this.
        with self.assertRaises(Exception):
            m.Data.query.filter_by(playbook_id=r_playbook.id).one()

    def test_record_with_no_value(self):
        """
        Trying to use ara_record with no value parameter should properly fail
        """
        task = MagicMock(Task)
        task.async = MagicMock()
        task.args = {
            'key': 'test-key',
        }

        action = ara_record.ActionModule(task, self.connection,
                                         self.play_context, loader=None,
                                         templar=None, shared_loader_obj=None)
        action.run()

        r_playbook = m.Playbook.query.first()
        self.assertIsNotNone(r_playbook)

        # There is no exception raised in the action module, we instead
        # properly return a failure status to Ansible.
        # If there is a failure, no data will be recorded so we can catch this.
        with self.assertRaises(Exception):
            m.Data.query.filter_by(playbook_id=r_playbook.id).one()
