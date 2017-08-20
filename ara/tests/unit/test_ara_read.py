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
import ara.plugins.actions.ara_read as ara_read
import ara.plugins.actions.ara_record as ara_record

from mock import Mock
from ara.tests.unit import fakes
from ara.tests.unit.common import TestAra


class TestRead(TestAra):
    """ Tests for the Ansible ara_read module """
    def setUp(self):
        super(TestRead, self).setUp()

    def tearDown(self):
        super(TestRead, self).tearDown()

    def test_read_record_with_playbook(self):
        """
        Read an existing record with ara_read for a specified playbook
        """
        ctx = fakes.FakeRun(record_task=False)
        play_context = Mock()
        play_context.check_mode = False
        connection = Mock()

        # Record something first
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

        action = ara_record.ActionModule(task, connection, play_context,
                                         loader=None, templar=None,
                                         shared_loader_obj=None)
        action.run()

        # Now read the data
        record_data = {
            'playbook': ctx.playbook['id'],
            'key': 'test-key',
        }
        task = fakes.AnsibleTask(
            name='Read something',
            action='ara_read',
            path='%s:%s' % (ctx.playbook['path'], 1),
            args=record_data
        )

        action = ara_read.ActionModule(task, connection, play_context,
                                       loader=None, templar=None,
                                       shared_loader_obj=None)
        data = action.run()

        r_data = m.Record.query.filter_by(playbook_id=ctx.playbook['id'],
                                          key='test-key').one()
        self.assertEqual(r_data.playbook_id, ctx.playbook['id'])
        self.assertEqual(r_data.key, 'test-key')
        self.assertEqual(r_data.value, 'test-value-outside-playbook')
        self.assertEqual(r_data.type, 'text')

        self.assertEqual(data['playbook_id'], r_data.playbook_id)
        self.assertEqual(data['key'], r_data.key)
        self.assertEqual(data['value'], r_data.value)
        self.assertEqual(data['type'], r_data.type)

    def test_read_record(self):
        """
        Read an existing record with ara_read
        """
        ctx = fakes.FakeRun(record_task=True, record_data={
            'key': 'test-key',
            'value': 'test-value-inside-playbook',
            'type': 'text'
        })
        play_context = Mock()
        play_context.check_mode = False
        connection = Mock()

        record_data = {
            'key': 'test-key',
        }
        task = fakes.AnsibleTask(
            name='Read something',
            action='ara_read',
            path='%s:%s' % (ctx.playbook['path'], 1),
            args=record_data
        )

        action = ara_read.ActionModule(task, connection, play_context,
                                       loader=None, templar=None,
                                       shared_loader_obj=None)
        data = action.run()

        r_data = m.Record.query.filter_by(playbook_id=ctx.playbook['id'],
                                          key='test-key').one()

        self.assertIsNotNone(r_data)
        self.assertEqual(r_data.playbook_id, ctx.playbook['id'])
        self.assertEqual(r_data.key, 'test-key')
        self.assertEqual(r_data.value, 'test-value-inside-playbook')
        self.assertEqual(r_data.type, 'text')

        self.assertEqual(data['playbook_id'], r_data.playbook_id)
        self.assertEqual(data['key'], r_data.key)
        self.assertEqual(data['value'], r_data.value)
        self.assertEqual(data['type'], r_data.type)

    def test_read_record_with_no_key(self):
        """
        Read a existing record that does not exist with ara_read
        """
        ctx = fakes.FakeRun(record_task=True)
        play_context = Mock()
        play_context.check_mode = False
        connection = Mock()

        record_data = {
            'key': 'key',
        }
        task = fakes.AnsibleTask(
            name='Read something',
            action='ara_read',
            path='%s:%s' % (ctx.playbook['path'], 1),
            args=record_data
        )

        action = ara_read.ActionModule(task, connection, play_context,
                                       loader=None, templar=None,
                                       shared_loader_obj=None)
        data = action.run()

        # There is no exception raised in the action module, we instead
        # properly return a failure status to Ansible.
        # If there is a failure, no data will be returned so we can catch this.
        with self.assertRaises(Exception):
            m.Record.query.filter_by(playbook_id=ctx.playbook['id'],
                                     key='key').one()

        self.assertEqual(data['failed'], True)
        self.assertEqual(data['playbook_id'], None)
        self.assertEqual(data['key'], None)
        self.assertEqual(data['value'], None)
