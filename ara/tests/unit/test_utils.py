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

from oslo_serialization import jsonutils

import ara.db.models as m
import ara.utils as u

from ara.tests.unit.common import TestAra
from ara.tests.unit.fakes import FakeRun


class TestUtils(TestAra):
    """ Tests the utils module """
    def setUp(self):
        super(TestUtils, self).setUp()
        self.env = self.app.jinja_env

    def tearDown(self):
        super(TestUtils, self).tearDown()

    def test_get_summary_stats_complete(self):
        # TODO: Switch this to API once views are using API
        ctx = FakeRun()
        playbook = m.Playbook.query.get(ctx.playbook['id'])
        res = u.get_summary_stats([playbook], 'playbook_id')

        self.assertEqual(4, res[playbook.id]['ok'])
        self.assertEqual(2, res[playbook.id]['changed'])
        self.assertEqual(1, res[playbook.id]['failed'])
        self.assertEqual(2, res[playbook.id]['skipped'])
        self.assertEqual(1, res[playbook.id]['unreachable'])
        self.assertEqual('failed', res[playbook.id]['status'])

    def test_get_summary_stats_incomplete(self):
        # TODO: Switch this to API once views are using API
        ctx = FakeRun(completed=False)
        playbook = m.Playbook.query.get(ctx.playbook['id'])
        res = u.get_summary_stats([playbook], 'playbook_id')

        self.assertEqual(0, res[playbook.id]['ok'])
        self.assertEqual(0, res[playbook.id]['changed'])
        self.assertEqual(0, res[playbook.id]['failed'])
        self.assertEqual(0, res[playbook.id]['skipped'])
        self.assertEqual(0, res[playbook.id]['unreachable'])
        self.assertEqual('incomplete', res[playbook.id]['status'])

    def test_fast_count(self):
        FakeRun()
        query = m.Task.query

        normal_count = query.count()
        fast_count = u.fast_count(query)

        self.assertEqual(normal_count, fast_count)

    def test_playbook_treeview(self):
        ctx = FakeRun()
        treeview = jsonutils.loads(u.playbook_treeview(ctx.playbook['id']))

        # ansible_run provides two fake files:
        # /some/path/main.yml and /playbook.yml
        for f in treeview:
            if f['text'] == 'some':
                self.assertEqual(f['text'], 'some')
                child = f['nodes'][0]
                self.assertEqual(child['text'], 'path')
                child = child['nodes'][0]
                self.assertEqual(child['text'], 'main.yml')
                self.assertEqual(child['dataAttr']['load'],
                                 ctx.playbook['files'][1]['id'])
            else:
                self.assertEqual(f['text'], 'playbook.yml')
                self.assertEqual(f['dataAttr']['load'],
                                 ctx.playbook['files'][0]['id'])
