from flask.ext.testing import TestCase
from collections import defaultdict
import random

import ara.webapp as w
import ara.models as m
import ara.utils as u
import ara.plugins.callbacks.log_ara as l

from mock import Mock


class Playbook(object):
    def __init__(self, path):
        self._file_name = path
        self.path = path


class Play(object):
    def __init__(self, name):
        self.name = name


class Task(object):
    def __init__(self, name, path, lineno=1, action='fakeaction'):
        self.name = name
        self.action = action
        self.path = '%s:%d' % (path, lineno)

    def get_path(self):
        return self.path


class TaskResult(object):
    def __init__(self, task, host, status, changed=False):
        assert status in ['ok', 'failed', 'skipped', 'unreachable']

        self.task = task
        self.status = status
        self._host = Mock()
        self._host.name = host
        self._result = {
            'changed': changed,
            'failed': status == 'failed',
            'skipped': status == 'skipped',
            'unreachable': status == 'unreachable',
        }


class Stats(object):
    def __init__(self, processed):
        self.processed = processed

    def summarize(self, name):
        return {
            'failures': self.processed[name]['failed'],
            'ok': self.processed[name]['ok'],
            'changed': self.processed[name]['changed'],
            'skipped': self.processed[name]['skipped'],
            'unreachable': self.processed[name]['unreachable'],
        }


class TestCallback(TestCase):
    '''Tests for the Ansible callback module'''

    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    TESTING = True

    def create_app(self):
        return w.create_app(self)

    def setUp(self):
        m.db.create_all()
        self.cb = l.CallbackModule()
        self.tag = '%04d' % random.randint(0, 9999)

        self.ansible_run()

    def tearDown(self):
        m.db.session.remove()
        m.db.drop_all()

    def ansible_run(self):
        '''Simulates an ansible run by creating stub versions of the
        information that Ansible passes to the callback, and then
        calling the various callback methods.'''

        self.playbook = self._test_playbook()
        self.play = self._test_play()
        self.task = self._test_task(self.playbook)
        self.results = [
            self._test_result(self.task, 'host1', 'ok', changed=True),
            self._test_result(self.task, 'host2', 'failed'),
        ]

        self.stats = self._test_stats()

    def _test_stats(self):
        stats = Stats({
            'host1': defaultdict(int, ok=1, changed=1),
            'host2': defaultdict(int, failed=1),
        })

        self.cb.v2_playbook_on_stats(stats)
        return stats

    def _test_result(self, task, host, status='ok', changed=False):
        result = TaskResult(task, host, status, changed)
        func = getattr(self.cb, 'v2_runner_on_%s' % status)
        func(result)
        return result

    def _test_playbook(self):
        path = '/test-playbook-%s.yml' % self.tag
        playbook = Playbook(path)
        self.cb.v2_playbook_on_start(playbook)
        return playbook

    def _test_play(self):
        name = 'test-play-%s' % self.tag
        play = Play(name)
        self.cb.v2_playbook_on_play_start(play)
        return play

    def _test_task(self, playbook):
        name = 'test-task-%s' % self.tag
        task = Task(name, playbook.path)
        self.cb.v2_playbook_on_task_start(task, False)
        return task

    def test_callback_playbook(self):
        r_playbook = m.Playbook.query.first()
        self.assertIsNotNone(r_playbook)
        self.assertEqual(r_playbook.path, self.playbook.path)

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
            self.assertIn(res.host.name, ['host1', 'host2'])
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
