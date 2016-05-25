from flask.ext.testing import TestCase
from collections import defaultdict
import random
import pytest

import ara.webapp as w
import ara.models as m
import ara.utils as u
from ara.models import db

from mock import Mock


class TestApp(TestCase):
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    TESTING = True

    def create_app(self):
        return w.create_app(self)

    def setUp(self):
        m.db.create_all()

        self.client = self.app.test_client()

    def tearDown(self):
        m.db.session.remove()
        m.db.drop_all()

    def ansible_run(self, complete=True):
        playbook = m.Playbook(path='testing.yml')
        play = m.Play(playbook=playbook, name='test play')
        task = m.Task(play=play, playbook=playbook,
                      action='test-action')
        host = m.Host(name='localhost')
        result = m.TaskResult(task=task, status='ok', host=host,
                              result='this is a test')

        self.ctx = dict(
            playbook=playbook,
            play=play,
            task=task,
            host=host,
            result=result)

        for obj in self.ctx.values():
            if hasattr(obj, 'start'):
                obj.start()
            db.session.add(obj)

        if complete:
            stats = m.Stats(playbook=playbook, host=host)
            self.ctx['stats'] = stats
            db.session.add(stats)

            for obj in self.ctx.values():
                if hasattr(obj, 'stop'):
                    obj.stop()

        db.session.commit()

    def test_overview(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)

    def test_list_host(self):
        self.ansible_run()
        res = self.client.get('/host/')
        self.assertEqual(res.status_code, 200)

    def test_list_playbook(self):
        self.ansible_run()
        res = self.client.get('/playbook/')
        self.assertEqual(res.status_code, 200)

    def test_list_playbook_incomplete(self):
        self.ansible_run(complete=False)
        res = self.client.get('/playbook/')
        self.assertEqual(res.status_code, 200)

    @pytest.mark.complete
    def test_show_playbook(self):
        self.ansible_run()
        res = self.client.get('/playbook/{}'.format(
            self.ctx['playbook'].id))
        self.assertEqual(res.status_code, 200)

    @pytest.mark.incomplete
    def test_show_playbook_incomplete(self):
        self.ansible_run(complete=False)
        res = self.client.get('/playbook/{}'.format(
            self.ctx['playbook'].id))
        self.assertEqual(res.status_code, 200)

    @pytest.mark.complete
    def test_show_play(self):
        self.ansible_run()
        res = self.client.get('/play/{}'.format(
            self.ctx['play'].id))
        self.assertEqual(res.status_code, 200)

    @pytest.mark.incomplete
    def test_show_play_incomplete(self):
        self.ansible_run(complete=False)
        res = self.client.get('/play/{}'.format(
            self.ctx['play'].id))
        self.assertEqual(res.status_code, 200)

    @pytest.mark.complete
    def test_show_task(self):
        self.ansible_run()
        res = self.client.get('/task/{}'.format(
            self.ctx['task'].id))
        self.assertEqual(res.status_code, 200)

    @pytest.mark.incomplete
    def test_show_task_incomplete(self):
        self.ansible_run(complete=False)
        res = self.client.get('/task/{}'.format(
            self.ctx['task'].id))
        self.assertEqual(res.status_code, 200)

    @pytest.mark.complete
    def test_show_host(self):
        self.ansible_run()
        res = self.client.get('/host/{}'.format(
            self.ctx['host'].id))
        self.assertEqual(res.status_code, 200)

    @pytest.mark.incomplete
    def test_show_host_incomplete(self):
        self.ansible_run(complete=False)
        res = self.client.get('/host/{}'.format(
            self.ctx['host'].id))
        self.assertEqual(res.status_code, 200)

    @pytest.mark.complete
    def test_show_result(self):
        self.ansible_run()
        res = self.client.get('/result/{}'.format(
            self.ctx['result'].id))
        self.assertEqual(res.status_code, 200)

    @pytest.mark.incomplete
    def test_show_result_incomplete(self):
        self.ansible_run(complete=False)
        res = self.client.get('/result/{}'.format(
            self.ctx['result'].id))
        self.assertEqual(res.status_code, 200)
