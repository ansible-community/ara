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
import os
import json

from ara.webapp import create_app
import ara.models as m
import ara.utils as u
import ara.plugins.callbacks.log_ara as l

from ara.tests.unit.common import TestAra
from ara.tests.unit import fakes

a = create_app()


class TestCallback(TestAra):
    """ Tests for the Ansible callback module """
    def setUp(self):
        super(TestCallback, self).setUp()

        self.cb = l.CallbackModule()
        self.tag = '%04d' % random.randint(0, 9999)

        self.ansible_run()

    def tearDown(self):
        super(TestCallback, self).tearDown()

    def ansible_run(self):
        """ Simulates an ansible run by creating stub versions of the
        information that Ansible passes to the callback, and then
        calling the various callback methods. """

        self.playbook = fakes.Playbook(path='/playbook-%s.yml' % self.tag)
        self.cb.v2_playbook_on_start(self.playbook)

        self.play = fakes.Play(playbook=self.playbook.model)
        self.cb.v2_playbook_on_play_start(self.play)

        self.task = fakes.Task(name='task-%s' % self.tag,
                               playbook=self.playbook.model,
                               path=self.playbook.path)
        self.cb.v2_playbook_on_task_start(self.task, False)

        self.host_one = fakes.Host(name='host1', playbook=self.playbook.model)
        self.host_two = fakes.Host(name='host2', playbook=self.playbook.model)
        self.results = [
            self._test_result(self.host_one, 'ok', changed=True),
            self._test_result(self.host_two, 'failed'),
        ]

        processed_stats = {
            self.host_one.name: defaultdict(int, ok=1, changed=1),
            self.host_two.name: defaultdict(int, failed=1)
        }
        self.stats = fakes.Stats(playbook=self.playbook.model,
                                 processed=processed_stats)
        self.cb.v2_playbook_on_stats(self.stats)

    def _test_result(self, host, status='ok', changed=False):
        result = fakes.TaskResult(task=self.task.model,
                                  host=host.model.name,
                                  status=status,
                                  changed=changed)
        func = getattr(self.cb, 'v2_runner_on_%s' % status)
        func(result)
        return result

    def test_callback_playbook(self):
        r_playbook = m.Playbook.query.first()
        self.assertIsNotNone(r_playbook)
        self.assertEqual(r_playbook.path, self.playbook.path)

    def test_playbook_persistence(self):
        r_playbook = m.Playbook.query.first()
        tmpfile = os.path.join(a.config['ARA_TMP_DIR'], 'ara.json')

        with open(tmpfile) as file:
            data = json.load(file)
        self.assertEqual(r_playbook.id, data['playbook']['id'])

    def test_callback_play(self):
        r_play = m.Play.query.first()
        self.assertIsNotNone(r_play)

        self.assertEqual(r_play.name, self.play.name)
        self.assertEqual(r_play.playbook.path, self.playbook.path)

    def test_callback_task(self):
        r_task = m.Task.query.first()
        self.assertIsNotNone(r_task)

        self.assertEqual(r_task.name, self.task.name)
        self.assertEqual(r_task.play.name, self.play.name)
        self.assertEqual(r_task.playbook.path, self.playbook.path)

    def test_callback_result(self):
        r_results = m.TaskResult.query.all()
        self.assertIsNotNone(r_results)

        for res in r_results:
            self.assertIn(res.host.name, [self.host_one.name,
                                          self.host_two.name])
            self.assertEqual(res.task.name, self.task.name)

    def test_callback_stats(self):
        r_stats = m.Stats.query.all()
        self.assertIsNotNone(r_stats)

        for stat in r_stats:
            self.assertEqual(stat.playbook.path, self.playbook.path)
            for status in ['ok', 'changed', 'failed',
                           'skipped', 'unreachable']:
                self.assertEqual(getattr(stat, status),
                                 self.stats.processed[stat.host.name][status])

    def test_summary_stats(self):
        r_hosts = m.Host.query.all()
        summary = u.get_summary_stats(r_hosts, 'host_id')
        for host in r_hosts:
            for status in ['ok', 'changed', 'failed',
                           'skipped', 'unreachable']:
                self.assertEqual(summary[host.id][status],
                                 self.stats.processed[host.name][status])
