import json

import ara.models as m

from common import TestAra


class TestModels(TestAra):
    '''Basic tests for database models'''
    def setUp(self):
        super(TestModels, self).setUp()

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

        self.data = m.Data(
            playbook=self.playbook,
            key='test key',
            value='test value'
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

        for obj in [self.playbook, self.play, self.task, self.data,
                    self.host, self.task_result, self.stats]:
            m.db.session.add(obj)

        m.db.session.commit()

    def tearDown(self):
        super(TestModels, self).tearDown()

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
