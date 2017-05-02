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

import ara.utils as u
import ara.models as m
import json

from ara.tests.unit.common import ansible_run
from ara.tests.unit.common import TestAra


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
        treeview = json.loads(u.playbook_treeview(ctx['playbook'].id))

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
                                 ctx['task_file'].id)
            else:
                self.assertEqual(f['text'], 'playbook.yml')
                self.assertEqual(f['dataAttr']['load'], ctx['pb_file'].id)
