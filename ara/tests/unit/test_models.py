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

from ara.tests.unit.fakes import FakeRun
from ara.tests.unit.common import TestAra


class TestModels(TestAra):
    """ Basic tests for database models """
    def setUp(self):
        super(TestModels, self).setUp()

        self.ctx = FakeRun()
        self.playbook = m.Playbook.query.get(self.ctx.playbook['id'])
        self.file = m.File.query.get(self.ctx.playbook['files'][0]['id'])
        self.content = m.FileContent.query.get(self.file.content.id)
        self.play = m.Play.query.get(self.ctx.play['id'])
        self.task = m.Task.query.get(self.ctx.t_ok['id'])
        self.result = m.Result.query.get(self.ctx.t_ok['results'][0]['id'])
        self.host = m.Host.query.get(self.result.host_id)
        self.record = m.Record.query.get(self.ctx.playbook['records'][0]['id'])

    def tearDown(self):
        super(TestModels, self).tearDown()

    def test_playbook(self):
        playbooks = m.Playbook.query.all()
        self.assertIn(self.playbook, playbooks)

    def test_playbook_file(self):
        file = (m.File.query
                .filter(m.File.playbook_id == self.playbook.id)
                .filter(m.File.is_playbook)).one()
        self.assertEqual(self.playbook.file, file)
        self.assertIn(file, self.playbook.files)

    def test_play(self):
        self.assertIn(self.play, self.playbook.plays)

    def test_task(self):
        self.assertIn(self.task, self.playbook.tasks)
        self.assertIn(self.task, self.play.tasks)
        self.assertIn(self.result, self.task.results)

    def test_file(self):
        self.assertIn(self.file, self.playbook.files)

    def test_duplicate_file(self):
        second = m.File(is_playbook=self.task.file.is_playbook,
                        path=self.task.file.path,
                        playbook=self.task.file.playbook,
                        content=self.task.file.content)
        m.db.session.add(second)

        with self.assertRaises(Exception):
            m.db.session.commit()

    def test_file_content(self):
        self.assertEqual(self.content.content,
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
        self.assertEqual(self.record.playbook_id, self.playbook.id)
        self.assertEqual(self.record.key, 'test-text')
        self.assertEqual(self.record.value, 'test-with-playbook')

    def test_duplicate_record(self):
        record = m.Record(
            playbook=self.playbook,
            key=self.record.key,
            value=self.record.value
        )
        m.db.session.add(record)

        with self.assertRaises(Exception):
            m.db.session.commit()

    def test_result(self):
        self.assertIn(self.result, self.playbook.results)
        self.assertIn(self.result, self.play.results)
        self.assertIn(self.result, self.task.results)

    def test_host(self):
        host1 = m.Host.query.filter_by(name=self.host.name).one()
        host2 = m.Host.query.get(self.host.id)

        self.assertEqual(host1, self.host)
        self.assertEqual(host2, self.host)

    def test_duplicate_host(self):
        host = m.Host(
            name=self.host.name,
            playbook=self.playbook,
        )
        m.db.session.add(host)

        with self.assertRaises(Exception):
            m.db.session.commit()
