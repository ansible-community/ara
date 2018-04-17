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

import ara.models as m

from ara.tests.unit.common import TestAra
from ara.tests.unit import fakes


class TestModels(TestAra):
    """ Basic tests for database models """
    def setUp(self):
        super(TestModels, self).setUp()

        self.playbook = fakes.Playbook(path='testing.yml',
                                       options={'option': 'test'}).model
        self.file = fakes.File(path=self.playbook.path,
                               playbook=self.playbook,
                               is_playbook=True).model
        content = fakes.FAKE_PLAYBOOK_CONTENT
        self.file_content = fakes.FileContent(content=content).model
        self.play = fakes.Play(name='test play',
                               playbook=self.playbook).model
        self.task = fakes.Task(name='test task',
                               play=self.play,
                               playbook=self.playbook,
                               tags=['just', 'testing']).model
        self.data = fakes.Data(playbook=self.playbook,
                               key='test key',
                               value='test value').model
        self.host = fakes.Host(name='localhost',
                               playbook=self.playbook).model
        self.host_facts = fakes.HostFacts(host=self.host).model
        self.task_result = fakes.TaskResult(task=self.task,
                                            status='ok',
                                            host=self.host).model
        self.stats = fakes.Stats(playbook=self.playbook,
                                 host=self.host,
                                 changed=0,
                                 failed=0,
                                 skipped=0,
                                 unreachable=0,
                                 ok=0).model

        for obj in [self.playbook, self.file, self.file_content, self.play,
                    self.task, self.data, self.host, self.host_facts,
                    self.task_result, self.stats]:
            m.db.session.add(obj)

        m.db.session.commit()

    def tearDown(self):
        super(TestModels, self).tearDown()

    def test_playbook(self):
        playbooks = m.Playbook.query.all()
        self.assertIn(self.playbook, playbooks)

    def test_playbook_file(self):
        playbook = m.Playbook.query.one()
        file = (m.File.query
                .filter(m.File.playbook_id == playbook.id)
                .filter(m.File.is_playbook)).one()
        self.assertEqual(playbook.file, file)

    def test_play(self):
        playbook = m.Playbook.query.get(self.playbook.id)
        self.assertIn(self.play, playbook.plays)

    def test_task(self):
        task = m.Task.query.get(self.task.id)
        assert task in self.playbook.tasks
        assert task in self.play.tasks

    def test_data(self):
        data = m.Data.query.get(self.data.id)
        self.assertEqual(data.playbook_id, self.playbook.id)
        self.assertEqual(data.key, 'test key')
        self.assertEqual(data.value, 'test value')

    def test_duplicate_data(self):
        data = m.Data(
            playbook=self.playbook,
            key='test key',
            value='another value'
        )
        m.db.session.add(data)

        with self.assertRaises(Exception):
            m.db.session.commit()

    def test_task_result(self):
        result = m.TaskResult.query.get(self.task_result.id)
        self.assertIn(result, self.task.task_results)

    def test_host(self):
        host1 = m.Host.query.filter_by(name='localhost').one()
        host2 = m.Host.query.get(self.host.id)

        self.assertEqual(host1, self.host)
        self.assertEqual(host2, self.host)

    def test_host_facts(self):
        host = m.Host.query.filter_by(name='localhost').one()
        facts = m.HostFacts.query.filter_by(host_id=host.id).one()
        facts_from_host = host.facts

        self.assertEqual(facts.values, facts_from_host.values)

    def test_duplicate_host(self):
        host = m.Host(
            name='localhost',
            playbook=self.playbook,
        )
        m.db.session.add(host)

        with self.assertRaises(Exception):
            m.db.session.commit()

    def test_stats(self):
        stats = m.Stats.query.get(self.stats.id)
        self.assertEqual(stats.host, self.host)
        self.assertEqual(stats.playbook, self.playbook)
