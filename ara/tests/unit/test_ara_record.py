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
import ara.plugins.actions.ara_record as ara_record

from ara.tests.unit import fakes
from ara.tests.unit.common import TestAra
from mock import Mock


class TestRecord(TestAra):
    """ Tests for the Ansible ara_record module """
    def setUp(self):
        super(TestRecord, self).setUp()

    def tearDown(self):
        super(TestRecord, self).tearDown()

    def test_create_text_record_with_playbook(self):
        """
        Create a new record with ara_record on a specified playbook
        """
        ctx = fakes.FakeRun(record_task=False)

        record_data = {
            'playbook': ctx.playbook['id'],
            'key': 'test-key',
            'value': 'test-value-outside-playbook',
            'type': 'text'
        }
        task = fakes.AnsibleTask(
            name='Record something',
            action='ara_record',
            path='%s:%s' % (ctx.playbook['path'], 1),
            args=record_data
        )

        play_context = Mock()
        play_context.check_mode = False
        connection = Mock()

        action = ara_record.ActionModule(task, connection, play_context,
                                         loader=None, templar=None,
                                         shared_loader_obj=None)
        action.run()

        r_data = m.Record.query.filter_by(playbook_id=ctx.playbook['id'],
                                          key='test-key').one()
        self.assertIsNotNone(r_data)
        self.assertEqual(r_data.playbook_id, ctx.playbook['id'])
        self.assertEqual(r_data.key, 'test-key')
        self.assertEqual(r_data.value, 'test-value-outside-playbook')
        self.assertEqual(r_data.type, 'text')

    def test_create_text_record(self):
        """
        Create a new record with ara_record.from inside a playbook run
        """
        ctx = fakes.FakeRun(record_task=True, record_data={
            'key': 'test-key',
            'value': 'test-value-inside-playbook',
            'type': 'text'
        })

        r_data = m.Record.query.filter_by(playbook_id=ctx.playbook['id'],
                                          key='test-key').one()
        self.assertIsNotNone(r_data)
        self.assertEqual(r_data.playbook_id, ctx.playbook['id'])
        self.assertEqual(r_data.key, 'test-key')
        self.assertEqual(r_data.value, 'test-value-inside-playbook')
        self.assertEqual(r_data.type, 'text')

    def test_create_url_record(self):
        """
        Create a new record with ara_record.
        """
        ctx = fakes.FakeRun(record_task=True, record_data={
            'key': 'test-url',
            'value': 'http://url',
            'type': 'url'
        })

        r_data = m.Record.query.filter_by(playbook_id=ctx.playbook['id'],
                                          key='test-url').one()
        self.assertIsNotNone(r_data)
        self.assertEqual(r_data.playbook_id, ctx.playbook['id'])
        self.assertEqual(r_data.key, 'test-url')
        self.assertEqual(r_data.value, 'http://url')
        self.assertEqual(r_data.type, 'url')

    def test_create_json_record(self):
        """
        Create a new record with ara_record.
        """
        ctx = fakes.FakeRun(record_task=True, record_data={
            'key': 'test-json',
            'value': '{"foo": "bar"}',
            'type': 'json'
        })

        r_data = m.Record.query.filter_by(playbook_id=ctx.playbook['id'],
                                          key='test-json').one()
        self.assertIsNotNone(r_data)
        self.assertEqual(r_data.playbook_id, ctx.playbook['id'])
        self.assertEqual(r_data.key, 'test-json')
        self.assertEqual(r_data.value, '{"foo": "bar"}')
        self.assertEqual(r_data.type, 'json')

    def test_create_list_record(self):
        """
        Create a new record with ara_record.
        """
        ctx = fakes.FakeRun(record_task=True, record_data={
            'key': 'test-list',
            'value': ['foo', 'bar'],
            'type': 'list'
        })

        r_data = m.Record.query.filter_by(playbook_id=ctx.playbook['id'],
                                          key='test-list').one()
        self.assertIsNotNone(r_data)
        self.assertEqual(r_data.playbook_id, ctx.playbook['id'])
        self.assertEqual(r_data.key, 'test-list')
        self.assertEqual(r_data.value, ['foo', 'bar'])
        self.assertEqual(r_data.type, 'list')

    def test_create_dict_record(self):
        """
        Create a new record with ara_record.
        """
        ctx = fakes.FakeRun(record_task=True, record_data={
            'key': 'test-dict',
            'value': {'foo': 'bar'},
            'type': 'dict'
        })

        r_data = m.Record.query.filter_by(playbook_id=ctx.playbook['id'],
                                          key='test-dict').one()
        self.assertIsNotNone(r_data)
        self.assertEqual(r_data.playbook_id, ctx.playbook['id'])
        self.assertEqual(r_data.key, 'test-dict')
        self.assertEqual(r_data.value, {'foo': 'bar'})
        self.assertEqual(r_data.type, 'dict')

    def test_create_record_with_no_type(self):
        """
        Create a new record with ara_record with no type specified.
        """
        ctx = fakes.FakeRun(record_task=True, record_data={
            'key': 'test-notype',
            'value': 'test-value'
        })

        r_data = m.Record.query.filter_by(playbook_id=ctx.playbook['id'],
                                          key='test-notype').one()
        self.assertIsNotNone(r_data)
        self.assertEqual(r_data.playbook_id, ctx.playbook['id'])
        self.assertEqual(r_data.key, 'test-notype')
        self.assertEqual(r_data.value, 'test-value')
        self.assertEqual(r_data.type, 'text')

    def test_create_record_as_wrong_type(self):
        """
        Create a new record with ara_record.
        """
        ctx = fakes.FakeRun(record_task=True, record_data={
            'key': 'test-wrongtype',
            'value': ['foo', 'bar'],
            'type': 'text'
        })

        r_data = m.Record.query.filter_by(playbook_id=ctx.playbook['id'],
                                          key='test-wrongtype').one()
        self.assertIsNotNone(r_data)
        self.assertEqual(r_data.playbook_id, ctx.playbook['id'])
        self.assertEqual(r_data.key, 'test-wrongtype')
        self.assertEqual(r_data.value, ['foo', 'bar'])
        self.assertEqual(r_data.type, 'text')

    def test_update_record(self):
        """
        Update an existing record by running ara_record a second time on the
        same key.
        """
        ctx = fakes.FakeRun(record_task=True, record_data={
            'key': 'test-update',
            'value': 'test-value',
            'type': 'text'
        })

        r_data = m.Record.query.filter_by(playbook_id=ctx.playbook['id'],
                                          key='test-update').one()
        self.assertIsNotNone(r_data)
        self.assertEqual(r_data.playbook_id, ctx.playbook['id'])
        self.assertEqual(r_data.key, 'test-update')
        self.assertEqual(r_data.value, 'test-value')
        self.assertEqual(r_data.type, 'text')

        record_data = {
            'key': 'test-update',
            'value': 'http://another-value',
            'type': 'url'
        }
        task = fakes.AnsibleTask(
            name='Record something',
            action='ara_record',
            path='%s:%s' % (ctx.playbook['path'], 1),
            args=record_data
        )

        play_context = Mock()
        play_context.check_mode = False
        connection = Mock()

        action = ara_record.ActionModule(task, connection, play_context,
                                         loader=None, templar=None,
                                         shared_loader_obj=None)
        action.run()

        r_data = m.Record.query.filter_by(playbook_id=ctx.playbook['id'],
                                          key='test-update').one()

        self.assertEqual(r_data.value, 'http://another-value')
        self.assertEqual(r_data.type, 'url')

    def test_record_with_no_key(self):
        """
        Trying to use ara_record with no key parameter should properly fail
        """
        ctx = fakes.FakeRun(record_task=True, record_data={
            'value': 'test-value',
        })

        # There is no exception raised in the action module, we instead
        # properly return a failure status to Ansible.
        # If there is a failure, no data will be recorded so we can catch this.
        with self.assertRaises(Exception):
            m.Record.query.filter_by(playbook_id=ctx.playbook['id']).one()

    def test_record_with_no_value(self):
        """
        Trying to use ara_record with no value parameter should properly fail
        """
        ctx = fakes.FakeRun(record_task=True, record_data={
            'key': 'test-key',
        })

        # There is no exception raised in the action module, we instead
        # properly return a failure status to Ansible.
        # If there is a failure, no data will be recorded so we can catch this.
        with self.assertRaises(Exception):
            m.Record.query.filter_by(playbook_id=ctx.playbook['id']).one()
