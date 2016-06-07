import json
import six

from flask.ext.testing import TestCase

import ara.webapp as w
import ara.models as m
import ara.cli.host
import ara.cli.play
import ara.cli.playbook
import ara.cli.result
import ara.cli.task
import ara.cli.stats

from common import ansible_run


class TestCLI(TestCase):
    '''Tests for the ARA CLI interface'''

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

    #################################
    # ara host <cmd>
    #################################
    def test_host_list(self):
        ctx = ansible_run()

        cmd = ara.cli.host.HostList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['-a'])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['host'].id)

    def test_host_list_for_playbook(self):
        ctx = ansible_run()

        cmd = ara.cli.host.HostList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--playbook', ctx['playbook'].id])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['host'].id)

    def test_host_list_for_non_existing_playbook(self):
        ansible_run()

        cmd = ara.cli.host.HostList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--playbook', 'foo'])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_host_show_by_id(self):
        ctx = ansible_run()

        cmd = ara.cli.host.HostShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([ctx['host'].id])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx['host'].id)

    def test_host_show_by_name(self):
        ctx = ansible_run()

        cmd = ara.cli.host.HostShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([
            '-b', ctx['host'].playbook.id, ctx['host'].name])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx['host'].id)

    def test_host_show_for_non_existing_host(self):
        ansible_run()

        cmd = ara.cli.host.HostShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['foo'])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)

    def test_host_fact_by_id(self):
        ctx = ansible_run()

        cmd = ara.cli.host.HostFacts(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([ctx['host'].id])
        res = cmd.take_action(args)

        facts = json.loads(ctx['facts'].values)
        self.assertEqual(res, zip(*sorted(six.iteritems(facts))))

    def test_host_fact_by_name(self):
        ctx = ansible_run()

        cmd = ara.cli.host.HostFacts(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([
            '-b', ctx['host'].playbook.id, ctx['host'].name])
        res = cmd.take_action(args)

        facts = json.loads(ctx['facts'].values)
        self.assertEqual(res, zip(*sorted(six.iteritems(facts))))

    def test_host_fact_non_existing_host(self):
        ctx = ansible_run()

        cmd = ara.cli.host.HostFacts(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args('foo')

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)

    def test_host_fact_existing_host_non_existing_facts(self):
        ctx = ansible_run(gather_facts=False)

        cmd = ara.cli.host.HostFacts(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([ctx['host'].id])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)

    #################################
    # ara play <cmd>
    #################################
    def test_play_list_all(self):
        ctx = ansible_run()

        cmd = ara.cli.play.PlayList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--all'])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['play'].id)

    def test_play_list_playbook(self):
        ctx = ansible_run()

        cmd = ara.cli.play.PlayList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--playbook', ctx['playbook'].id])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['play'].id)

    def test_play_list_non_existing_playbook(self):
        ctx = ansible_run()

        cmd = ara.cli.play.PlayList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--playbook', 'foo'])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_play_show(self):
        ctx = ansible_run()

        cmd = ara.cli.play.PlayShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([ctx['play'].id])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx['play'].id)

    def test_play_show_non_existing(self):
        ctx = ansible_run()

        cmd = ara.cli.play.PlayShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['foo'])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)

    #################################
    # ara playbook <cmd>
    #################################
    def test_playbook_list(self):
        ctx = ansible_run()

        cmd = ara.cli.playbook.PlaybookList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['playbook'].id)

    def test_playbook_list_complete(self):
        ctx = ansible_run()

        cmd = ara.cli.playbook.PlaybookList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--complete'])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['playbook'].id)

    def test_playbook_list_complete_with_no_complete(self):
        ctx = ansible_run(complete=False)

        cmd = ara.cli.playbook.PlaybookList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--complete'])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_playbook_list_incomplete(self):
        ctx = ansible_run(complete=False)

        cmd = ara.cli.playbook.PlaybookList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--incomplete'])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['playbook'].id)

    def test_playbook_list_incomplete_with_no_incomplete(self):
        ctx = ansible_run()

        cmd = ara.cli.playbook.PlaybookList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--incomplete'])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_playbook_show(self):
        ctx = ansible_run()

        cmd = ara.cli.playbook.PlaybookShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([ctx['playbook'].id])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx['playbook'].id)

    def test_playbook_show_non_existing(self):
        ctx = ansible_run()

        cmd = ara.cli.playbook.PlaybookShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['foo'])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)

    #################################
    # ara result <cmd>
    #################################
    def test_result_list_all(self):
        ctx = ansible_run()

        cmd = ara.cli.result.ResultList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--all'])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['result'].id)

    def test_result_list_playbook(self):
        ctx = ansible_run()

        cmd = ara.cli.result.ResultList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--playbook', ctx['playbook'].id])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['result'].id)

    def test_result_list_non_existing_playbook(self):
        ctx = ansible_run()

        cmd = ara.cli.result.ResultList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--playbook', 'foo'])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_result_list_play(self):
        ctx = ansible_run()

        cmd = ara.cli.result.ResultList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--play', ctx['play'].id])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['result'].id)

    def test_result_list_non_existing_play(self):
        ctx = ansible_run()

        cmd = ara.cli.result.ResultList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--play', 'foo'])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_result_list_task(self):
        ctx = ansible_run()

        cmd = ara.cli.result.ResultList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--task', ctx['task'].id])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['result'].id)

    def test_result_list_non_existing_task(self):
        ansible_run()

        cmd = ara.cli.result.ResultList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--task', 'foo'])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_result_show(self):
        ctx = ansible_run()

        cmd = ara.cli.result.ResultShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([ctx['result'].id])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx['result'].id)

    def test_result_show_non_existing(self):
        ansible_run()

        cmd = ara.cli.result.ResultShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['foo'])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)

    def test_result_show_long(self):
        ctx = ansible_run()

        cmd = ara.cli.result.ResultShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([ctx['result'].id, '--long'])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx['result'].id)
        self.assertEqual(res[1][-1], json.dumps(ctx['result'].result))

    def test_result_show_long_non_existing(self):
        ansible_run()

        cmd = ara.cli.result.ResultShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['foo', '--long'])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)

    #################################
    # ara task <cmd>
    #################################
    def test_task_list_all(self):
        ctx = ansible_run()

        cmd = ara.cli.task.TaskList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--all'])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['task'].id)

    def test_task_list_play(self):
        ctx = ansible_run()

        cmd = ara.cli.task.TaskList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--play', ctx['play'].id])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['task'].id)

    def test_task_list_non_existing_play(self):
        ctx = ansible_run()

        cmd = ara.cli.task.TaskList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--play', 'foo'])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_task_list_playbook(self):
        ctx = ansible_run()

        cmd = ara.cli.task.TaskList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--playbook', ctx['playbook'].id])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['task'].id)

    def test_task_list_non_existing_playbook(self):
        ctx = ansible_run()

        cmd = ara.cli.task.TaskList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--playbook', 'foo'])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_task_show(self):
        ctx = ansible_run()

        cmd = ara.cli.task.TaskShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([ctx['task'].id])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx['task'].id)

    def test_task_show_non_existing(self):
        ctx = ansible_run()

        cmd = ara.cli.task.TaskShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['foo'])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)

    #################################
    # ara stats <cmd>
    #################################
    def test_stats_list(self):
        ctx = ansible_run()

        cmd = ara.cli.stats.StatsList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['stats'].id)

    def test_stats_show(self):
        ctx = ansible_run()

        cmd = ara.cli.stats.StatsShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([ctx['stats'].id])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx['stats'].id)

    def test_stats_show_non_existing(self):
        ctx = ansible_run()

        cmd = ara.cli.stats.StatsShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['foo'])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)
