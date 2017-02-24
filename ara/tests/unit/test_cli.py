#   Copyright 2017 Red Hat, Inc. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

import json
import os
import shutil
import six
import tempfile

from lxml import etree

import ara.cli.data
import ara.cli.generate
import ara.cli.host
import ara.cli.play
import ara.cli.playbook
import ara.cli.result
import ara.cli.task
import ara.cli.stats
import ara.models as m

from ara.tests.unit.common import ansible_run
from ara.tests.unit.common import TestAra


class TestCLIData(TestAra):
    """ Tests for the ARA CLI data commands """
    def setUp(self):
        super(TestCLIData, self).setUp()

    def tearDown(self):
        super(TestCLIData, self).tearDown()

    def test_data_list(self):
        ctx = ansible_run(ara_record=True)

        cmd = ara.cli.data.DataList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['-a'])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['data'].id)

    def test_data_list_for_playbook(self):
        ctx = ansible_run(ara_record=True)

        cmd = ara.cli.data.DataList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--playbook', ctx['playbook'].id])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['data'].id)

    def test_data_list_for_non_existing_playbook(self):
        ansible_run(ara_record=True)

        cmd = ara.cli.data.DataList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--playbook', 'foo'])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_data_show_by_id(self):
        ctx = ansible_run(ara_record=True)

        cmd = ara.cli.data.DataShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([ctx['data'].id])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx['data'].id)

    def test_data_show_by_key(self):
        ctx = ansible_run(ara_record=True)

        cmd = ara.cli.data.DataShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([
            '-b', ctx['data'].playbook.id, ctx['data'].key])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx['data'].id)

    def test_data_show_for_non_existing_data(self):
        ansible_run(ara_record=True)

        cmd = ara.cli.data.DataShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['foo'])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)


class TestCLIHost(TestAra):
    """ Tests for the ARA CLI host commands """
    def setUp(self):
        super(TestCLIHost, self).setUp()

    def tearDown(self):
        super(TestCLIHost, self).tearDown()

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
        ansible_run()

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


class TestCLIPlay(TestAra):
    """ Tests for the ARA CLI play commands """
    def setUp(self):
        super(TestCLIPlay, self).setUp()

    def tearDown(self):
        super(TestCLIPlay, self).tearDown()

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
        ansible_run()

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
        ansible_run()

        cmd = ara.cli.play.PlayShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['foo'])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)


class TestCLIPlaybook(TestAra):
    """ Tests for the ARA CLI playbook commands """
    def setUp(self):
        super(TestCLIPlaybook, self).setUp()

    def tearDown(self):
        super(TestCLIPlaybook, self).tearDown()

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
        ansible_run(complete=False)

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
        ansible_run()

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
        ansible_run()

        cmd = ara.cli.playbook.PlaybookShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['foo'])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)


class TestCLIResult(TestAra):
    """ Tests for the ARA CLI result commands """
    def setUp(self):
        super(TestCLIResult, self).setUp()

    def tearDown(self):
        super(TestCLIResult, self).tearDown()

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
        ansible_run()

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
        ansible_run()

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


class TestCLITask(TestAra):
    """ Tests for the ARA CLI task commands """
    def setUp(self):
        super(TestCLITask, self).setUp()

    def tearDown(self):
        super(TestCLITask, self).tearDown()

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
        ansible_run()

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
        ansible_run()

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
        ansible_run()

        cmd = ara.cli.task.TaskShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['foo'])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)


class TestCLIStats(TestAra):
    """ Tests for the ARA CLI stats commands """
    def setUp(self):
        super(TestCLIStats, self).setUp()

    def tearDown(self):
        super(TestCLIStats, self).tearDown()

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
        ansible_run()

        cmd = ara.cli.stats.StatsShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['foo'])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)


class TestCLIGenerate(TestAra):
    """ Tests for the ARA CLI generate commands """
    def setUp(self):
        super(TestCLIGenerate, self).setUp()
        # Create a temporary directory for ara generate tests
        self.generate_dir = tempfile.mkdtemp(prefix='ara')

    def tearDown(self):
        super(TestCLIGenerate, self).tearDown()

        # Remove the temporary ara generate directory
        shutil.rmtree(self.generate_dir)

    def test_generate_html_no_destination(self):
        """ Ensures generating without a destination fails """
        ansible_run()

        cmd = ara.cli.generate.GenerateHtml(None, None)
        parser = cmd.get_parser('test')

        with self.assertRaises(SystemExit):
            args = parser.parse_args([])
            cmd.take_action(args)

    def test_generate_html(self):
        """ Roughly ensures the expected files are generated properly """
        dir = self.generate_dir

        ctx = ansible_run()
        cmd = ara.cli.generate.GenerateHtml(None, None)
        parser = cmd.get_parser('test')

        args = parser.parse_args([dir])
        cmd.take_action(args)

        file_id = ctx['task'].file_id
        host_id = ctx['host'].id
        result_id = ctx['result'].id
        paths = [
            os.path.join(dir, 'index.html'),
            os.path.join(dir, 'static'),
            os.path.join(dir, 'file/index.html'),
            os.path.join(dir, 'file/{0}'.format(file_id)),
            os.path.join(dir, 'host/index.html'),
            os.path.join(dir, 'host/{0}'.format(host_id)),
            os.path.join(dir, 'reports/index.html'),
            os.path.join(dir, 'playbook/index.html'),
            os.path.join(dir, 'result/index.html'),
            os.path.join(dir, 'result/{0}'.format(result_id))
        ]

        for path in paths:
            self.assertTrue(os.path.exists(path))

    def test_generate_html_for_playbook(self):
        """ Roughly ensures the expected files are generated properly """
        dir = self.generate_dir

        # Record two separate playbooks
        ctx = ansible_run()
        ansible_run()
        cmd = ara.cli.generate.GenerateHtml(None, None)
        parser = cmd.get_parser('test')

        args = parser.parse_args([dir, '--playbook', ctx['playbook'].id])
        cmd.take_action(args)

        file_id = ctx['task'].file_id
        host_id = ctx['host'].id
        result_id = ctx['result'].id
        paths = [
            os.path.join(dir, 'index.html'),
            os.path.join(dir, 'static'),
            os.path.join(dir, 'file/index.html'),
            os.path.join(dir, 'file/{0}'.format(file_id)),
            os.path.join(dir, 'host/index.html'),
            os.path.join(dir, 'host/{0}'.format(host_id)),
            os.path.join(dir, 'reports/index.html'),
            os.path.join(dir, 'playbook/index.html'),
            os.path.join(dir, 'result/index.html'),
            os.path.join(dir, 'result/{0}'.format(result_id))
        ]

        for path in paths:
            self.assertTrue(os.path.exists(path))

        # Test that we effectively have two playbooks
        playbooks = m.Playbook.query.all()
        self.assertTrue(len(playbooks) == 2)

        # Retrieve the other playbook and validate that we haven't generated
        # files for it
        playbook_two = (m.Playbook.query
                        .filter(m.Playbook.id != ctx['playbook'].id).one())
        path = os.path.join(dir, 'playbook/{0}'.format(playbook_two.id))
        self.assertFalse(os.path.exists(path))

    def test_generate_junit(self):
        """ Roughly ensures the expected xml is generated properly """
        tdir = self.generate_dir

        ctx = ansible_run()
        cmd = ara.cli.generate.GenerateJunit(None, None)
        parser = cmd.get_parser('test')

        junit_file = '{tdir}/junit.xml'.format(tdir=tdir)
        args = parser.parse_args([junit_file])
        cmd.take_action(args)

        self.assertTrue(os.path.exists(junit_file))

        tasks = m.Task.query.all()
        tree = etree.parse(junit_file)
        self.assertEqual(tree.getroot().tag, "testsuites")
        self.assertEqual(tree.getroot()[0].tag, "testsuite")
        self.assertEqual(tree.getroot()[0][0].tag, "testcase")
        self.assertEqual(int(tree.getroot().get('tests')), len(tasks))
        self.assertEqual(int(tree.getroot().get('failures')),
                         ctx['stats'].failed)

    def test_generate_junit_for_playbook(self):
        """ Roughly ensures the expected xml is generated properly """
        tdir = self.generate_dir

        # Record two separate playbooks
        ctx = ansible_run()
        ansible_run()
        cmd = ara.cli.generate.GenerateJunit(None, None)
        parser = cmd.get_parser('test')

        junit_file = "{tdir}/junit-playbook.xml".format(tdir=tdir)
        playbook = ctx['playbook'].id
        args = parser.parse_args([junit_file, '--playbook', playbook])
        cmd.take_action(args)

        # Test that we effectively have two playbooks
        playbooks = m.Playbook.query.all()
        all_tasks = m.Task.query.all()
        tasks = (m.Task.query
                 .filter(m.Task.playbook_id == ctx['playbook'].id).all())
        self.assertEqual(len(playbooks), 2)
        self.assertNotEqual(len(all_tasks), len(tasks))

        self.assertTrue(os.path.exists(junit_file))

        tree = etree.parse(junit_file)
        self.assertEqual(tree.getroot().tag, "testsuites")
        self.assertEqual(tree.getroot()[0].tag, "testsuite")
        self.assertEqual(tree.getroot()[0][0].tag, "testcase")
        self.assertEqual(int(tree.getroot().get('tests')), len(tasks))
