import json
import six

from flask.ext.testing import TestCase

import ara.webapp as w
import ara.models as m
import ara.cli.playbook
import ara.cli.host

from common import ansible_run

class TestCLI(TestCase):
    '''Tests for the ARA web interface'''

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

    def test_playbook_list(self):
        ctx = ansible_run()

        cmd = ara.cli.playbook.PlaybookList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['playbook'].id)

    def test_playbook_show(self):
        ctx = ansible_run()

        cmd = ara.cli.playbook.PlaybookShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([ctx['playbook'].id])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx['playbook'].id)

    def test_host_fact(self):
        ctx = ansible_run()

        cmd = ara.cli.host.HostFacts(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([ctx['host'].id])
        res = cmd.take_action(args)

        facts = json.loads(ctx['facts'].values)
        self.assertEqual(res, zip(*sorted(six.iteritems(facts))))
