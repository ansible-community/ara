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

import ara.utils as u
import ara.models as m

from ara.tests.unit.common import ansible_run
from ara.tests.unit.common import TestAra
from oslo_serialization import jsonutils


class TestUtils(TestAra):
    """ Tests the utils module """
    def setUp(self):
        super(TestUtils, self).setUp()
        self.env = self.app.jinja_env

    def tearDown(self):
        super(TestUtils, self).tearDown()

    def test_get_summary_stats_complete(self):
        ctx = ansible_run()
        playbook = ctx['playbook'].id
        res = u.get_summary_stats([ctx['playbook']], 'playbook_id')

        self.assertEqual(1, res[playbook]['ok'])
        self.assertEqual(1, res[playbook]['changed'])
        self.assertEqual(0, res[playbook]['failed'])
        self.assertEqual(1, res[playbook]['skipped'])
        self.assertEqual(0, res[playbook]['unreachable'])
        self.assertEqual('success', res[playbook]['status'])

    def test_get_summary_stats_incomplete(self):
        ctx = ansible_run(complete=False)
        playbook = ctx['playbook'].id
        res = u.get_summary_stats([ctx['playbook']], 'playbook_id')

        self.assertEqual(0, res[playbook]['ok'])
        self.assertEqual(0, res[playbook]['changed'])
        self.assertEqual(0, res[playbook]['failed'])
        self.assertEqual(0, res[playbook]['skipped'])
        self.assertEqual(0, res[playbook]['unreachable'])
        self.assertEqual('incomplete', res[playbook]['status'])

    def test_get_summary_stats_failed(self):
        ctx = ansible_run(failed=True)
        playbook = ctx['playbook'].id
        res = u.get_summary_stats([ctx['playbook']], 'playbook_id')

        self.assertEqual(1, res[playbook]['ok'])
        self.assertEqual(1, res[playbook]['changed'])
        self.assertEqual(1, res[playbook]['failed'])
        self.assertEqual(1, res[playbook]['skipped'])
        self.assertEqual(0, res[playbook]['unreachable'])
        self.assertEqual('failed', res[playbook]['status'])

    def test_fast_count(self):
        ansible_run()
        query = m.Task.query

        normal_count = query.count()
        fast_count = u.fast_count(query)

        self.assertEqual(normal_count, fast_count)

    def test_playbook_treeview(self):
        ctx = ansible_run()
        treeview = jsonutils.loads(u.playbook_treeview(ctx['playbook'].id))

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
                                 ctx['task_file'].id + '/')
            else:
                self.assertEqual(f['text'], 'playbook.yml')
                self.assertEqual(
                    f['dataAttr']['load'], ctx['pb_file'].id + '/'
                )
