import json

from flask.ext.testing import TestCase

import ara.webapp as w
import ara.models as m


class TestModels(TestCase):
    '''Basic tests for database models'''

    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    TESTING = True

    def create_app(self):
        return w.create_app(self)

    def setUp(self):
        m.db.create_all()

        self.playbook = m.Playbook(path='testing.yml')

        self.play = m.Play(
            name='test play',
            playbook=self.playbook,
        )

        self.task = m.Task(
            name='test task',
            play=self.play,
            playbook=self.playbook,
        )

        self.host = m.Host(
            name='localhost',
            playbook=self.playbook,
        )

        self.host_facts = m.HostFacts(
            host=self.host,
            values=json.dumps('{"fact": "value"}')
        )

        self.task_result = m.TaskResult(
            task=self.task,
            status='ok',
            host=self.host,
        )

        self.stats = m.Stats(
            playbook=self.playbook,
            host=self.host,
            changed=0,
            failed=0,
            skipped=0,
            unreachable=0,
            ok=0,
        )

        for obj in [self.playbook, self.play, self.task,
                    self.host, self.task_result, self.stats]:
            m.db.session.add(obj)

        m.db.session.commit()

    def tearDown(self):
        m.db.session.remove()
        m.db.drop_all()

    def test_playbook(self):
        playbooks = m.Playbook.query.all()
        self.assertIn(self.playbook, playbooks)

    def test_play(self):
        playbook = m.Playbook.query.get(self.playbook.id)
        self.assertIn(self.play, playbook.plays)

    def test_task(self):
        task = m.Task.query.get(self.task.id)
        assert task in self.playbook.tasks
        assert task in self.play.tasks

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
