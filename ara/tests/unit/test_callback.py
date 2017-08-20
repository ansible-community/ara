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
import ara.utils as u

from ara.tests.unit import fakes
from ara.tests.unit.common import TestAra


class TestCallback(TestAra):
    """ Tests for the Ansible callback module """
    def setUp(self):
        super(TestCallback, self).setUp()
        self.ctx = fakes.FakeRun()

    def tearDown(self):
        super(TestCallback, self).tearDown()

    def test_callback_playbook(self):
        r_playbook = m.Playbook.query.first()
        self.assertIsNotNone(r_playbook)
        self.assertEqual(r_playbook.path, self.ctx.playbook['path'])

    def test_callback_play(self):
        r_play = m.Play.query.first()
        self.assertIsNotNone(r_play)

        self.assertEqual(r_play.name, self.ctx.play['name'])
        self.assertEqual(r_play.playbook.path, self.ctx.playbook['path'])

    def test_callback_task(self):
        r_task = m.Task.query.first()
        self.assertIsNotNone(r_task)

        self.assertEqual(r_task.name, self.ctx.t_ok['name'])
        self.assertEqual(r_task.play.name, self.ctx.play['name'])
        self.assertEqual(r_task.playbook.path, self.ctx.playbook['path'])

    def test_callback_result(self):
        r_results = m.Result.query.filter_by(skipped=True).all()
        self.assertIsNotNone(r_results)

        for res in r_results:
            self.assertIn(res.host.name, [self.ctx.host_one.name,
                                          self.ctx.host_two.name])
            self.assertEqual(res.task.name, self.ctx.t_skipped['name'])

    def test_callback_stats(self):
        r_hosts = m.Host.query.all()
        self.assertIsNotNone(r_hosts)

        for host in r_hosts:
            self.assertEqual(host.playbook.path, self.ctx.playbook['path'])
            for status in ['ok', 'changed', 'failed',
                           'skipped', 'unreachable']:
                self.assertEqual(getattr(host, status),
                                 self.ctx.stats.processed[host.name][status])

    def test_summary_stats(self):
        r_hosts = m.Host.query.all()
        summary = u.get_summary_stats(r_hosts, 'id')
        for host in r_hosts:
            for status in ['ok', 'changed', 'failed',
                           'skipped', 'unreachable']:
                self.assertEqual(summary[host.id][status],
                                 self.ctx.stats.processed[host.name][status])
