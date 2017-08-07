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

from ara.tests.unit import fakes
from ara.tests.unit.common import TestAra


class TestModels(TestAra):
    """ Basic tests for database models """
    def setUp(self):
        super(TestModels, self).setUp()

        self.playbook = fakes.Playbook(path='testing.yml',
                                       parameters={'option': 'test'}).model
        self.playbook_content = fakes.FileContent(
            content=fakes.FAKE_PLAYBOOK_CONTENT
        ).model
        self.playbook_file = fakes.File(path=self.playbook.path,
                                        playbook=self.playbook,
                                        is_playbook=True,
                                        content=self.playbook_content).model

        self.play = fakes.Play(name='test play',
                               playbook=self.playbook).model

        self.task_content = fakes.FileContent(
            content=fakes.FAKE_TASK_CONTENT
        ).model
        self.task_file = fakes.File(path='main.yml',
                                    playbook=self.playbook,
                                    is_playbook=False,
                                    content=self.task_content).model
        self.task = fakes.Task(name='test task',
                               play=self.play,
                               playbook=self.playbook,
                               file=self.task_file,
                               action='fake_action',
                               tags=['just', 'testing']).model

        self.record = fakes.Record(playbook=self.playbook,
                                   key='test key',
                                   value='test value').model

        self.host = fakes.Host(name='localhost',
                               playbook=self.playbook).model
        self.host_facts = fakes.HostFacts(host=self.host).model

        self.result = fakes.Result(playbook=self.playbook,
                                   play=self.play,
                                   task=self.task,
                                   status='ok',
                                   host=self.host).model

        self.stats = fakes.Stats(playbook=self.playbook,
                                 host=self.host,
                                 changed=0,
                                 failed=0,
                                 skipped=0,
                                 unreachable=0,
                                 ok=0).model

        for obj in [self.playbook, self.playbook_file, self.play,
                    self.task, self.record, self.host, self.host_facts,
                    self.result, self.stats]:
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
        self.assertIn(file, playbook.files)

    def test_play(self):
        playbook = m.Playbook.query.get(self.playbook.id)
        self.assertIn(self.play, playbook.plays)

    def test_task(self):
        task = m.Task.query.get(self.task.id)
        self.assertIn(task, self.playbook.tasks)
        self.assertIn(task, self.play.tasks)

    def test_file(self):
        file = m.File.query.get(self.playbook_file.id)
        self.assertIn(file, self.playbook.files)

    def test_duplicate_file(self):
        second = m.File(is_playbook=self.task_file.is_playbook,
                        path=self.task_file.path,
                        playbook=self.task_file.playbook,
                        content=self.task_file.content)
        m.db.session.add(second)

        with self.assertRaises(Exception):
            m.db.session.commit()

    def test_file_content(self):
        file_content = m.FileContent.query.get(self.playbook.file.content.id)
        self.assertEqual(file_content.content,
                         self.playbook.file.content.content)

    def test_duplicate_file_content(self):
        # Two files with the same content should yield the same sha1
        file_content = m.FileContent.query.get(self.task.file.content.id)
        second = m.File(is_playbook=self.task.file.is_playbook,
                        path='/anotherpath.yml',
                        playbook=self.task.file.playbook,
                        content=self.task.file.content)
        m.db.session.add(second)
        m.db.session.commit()
        self.assertEqual(file_content.id, second.content.id)
        self.assertEqual(file_content.sha1, second.content.sha1)
        self.assertEqual(file_content.content, second.content.content)

    def test_record(self):
        record = m.Record.query.get(self.record.id)
        self.assertEqual(record.playbook_id, self.playbook.id)
        self.assertEqual(record.key, 'test key')
        self.assertEqual(record.value, 'test value')

    def test_duplicate_record(self):
        record = m.Record(
            playbook=self.playbook,
            key='test key',
            value='another value'
        )
        m.db.session.add(record)

        with self.assertRaises(Exception):
            m.db.session.commit()

    def test_result(self):
        result = m.Result.query.get(self.result.id)
        self.assertIn(result, self.playbook.results)
        self.assertIn(result, self.play.results)
        self.assertIn(result, self.task.results)

    def test_host(self):
        host1 = m.Host.query.filter_by(name='localhost').one()
        host2 = m.Host.query.get(self.host.id)

        self.assertEqual(host1, self.host)
        self.assertEqual(host2, self.host)
        self.assertIn(self.stats.host_id, [host1.id, host2.id])

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
