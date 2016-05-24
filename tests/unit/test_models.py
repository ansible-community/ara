from flask.ext.testing import TestCase

import ara.webapp as w
import ara.models as m


class TestModels(TestCase):
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    TESTING = True

    def create_app(self):
        return w.create_app(self)

    def setUp(self):
        m.db.create_all()

    def tearDown(self):
        m.db.session.remove()
        m.db.drop_all()

    def test_playbook(self):
        playbook = m.Playbook(path='testing.yml')
        m.db.session.add(playbook)
        m.db.session.commit()

        playbooks = m.Playbook.query.all()
        assert playbook in playbooks

    def test_play(self):
        playbook = m.Playbook(path='testing.yml')
        play = m.Play(name='test play', playbook=playbook)
        m.db.session.add(play)
        m.db.session.commit()

        playbook = m.Playbook.query.get(playbook.id)
        assert play in playbook.plays

    def test_task(self):
        playbook = m.Playbook(path='testing.yml')
        play = m.Play(name='test play', playbook=playbook)
        task = m.Task(name='test task', play=play, playbook=playbook)

        m.db.session.add(task)
        m.db.session.commit()

        task = m.Task.query.get(task.id)
        assert task in playbook.tasks
        assert task in play.tasks
