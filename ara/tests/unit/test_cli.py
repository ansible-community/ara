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

import os
import six

from glob import glob
from lxml import etree
from oslo_serialization import jsonutils
from subunit._to_disk import to_disk

import ara.shell
import ara.cli.record
import ara.cli.generate
import ara.cli.host
import ara.cli.play
import ara.cli.playbook
import ara.cli.result
import ara.cli.task

from ara.api.files import FileApi
from ara.api.hosts import HostApi
from ara.api.plays import PlayApi
from ara.api.playbooks import PlaybookApi
from ara.api.records import RecordApi
from ara.api.results import ResultApi
from ara.api.tasks import TaskApi

from ara.tests.unit.fakes import FakeRun
from ara.tests.unit.common import TestAra


class TestCLIRecord(TestAra):
    """ Tests for the ARA CLI record commands """
    def setUp(self):
        super(TestCLIRecord, self).setUp()
        self.client = RecordApi()

    def tearDown(self):
        super(TestCLIRecord, self).tearDown()

    def test_record_list(self):
        ctx = FakeRun()

        cmd = ara.cli.record.RecordList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['-a'])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx.playbook['records'][0]['id'])

    def test_record_list_for_playbook(self):
        ctx = FakeRun()

        cmd = ara.cli.record.RecordList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([
            '--playbook',
            six.text_type(ctx.playbook['id'])
        ])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx.playbook['records'][0]['id'])

    def test_record_list_for_non_existing_playbook(self):
        cmd = ara.cli.record.RecordList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--playbook', six.text_type(9)])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_record_show_by_id(self):
        ctx = FakeRun()

        cmd = ara.cli.record.RecordShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([
            six.text_type(ctx.playbook['records'][0]['id'])
        ])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx.playbook['records'][0]['id'])

    def test_record_show_by_key(self):
        ctx = FakeRun()

        # Get record
        resp, record = self.client.get(id=ctx.playbook['records'][0]['id'])

        cmd = ara.cli.record.RecordShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([
            '-b',
            six.text_type(ctx.playbook['id']),
            record['key']
        ])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], record['id'])

    def test_record_show_for_non_existing_data(self):
        cmd = ara.cli.record.RecordShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([0])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)


class TestCLIHost(TestAra):
    """ Tests for the ARA CLI host commands """
    def setUp(self):
        super(TestCLIHost, self).setUp()
        self.client = HostApi()

    def tearDown(self):
        super(TestCLIHost, self).tearDown()

    def test_host_list(self):
        ctx = FakeRun()

        cmd = ara.cli.host.HostList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['-a'])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx.playbook['hosts'][0]['id'])

    def test_host_list_for_playbook(self):
        ctx = FakeRun()

        cmd = ara.cli.host.HostList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([
            '--playbook',
            six.text_type(ctx.playbook['id'])
        ])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx.playbook['hosts'][0]['id'])

    def test_host_list_for_non_existing_playbook(self):
        cmd = ara.cli.host.HostList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--playbook', six.text_type(9)])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_host_show_by_id(self):
        ctx = FakeRun()

        cmd = ara.cli.host.HostShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([
            six.text_type(ctx.playbook['hosts'][0]['id'])
        ])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx.playbook['hosts'][0]['id'])

    def test_host_show_by_name(self):
        ctx = FakeRun()

        # Get host
        resp, host = self.client.get(id=ctx.playbook['hosts'][0]['id'])

        cmd = ara.cli.host.HostShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([
            '-b',
            six.text_type(ctx.playbook['id']),
            host['name']
        ])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], host['id'])

    def test_host_show_for_non_existing_host(self):
        cmd = ara.cli.host.HostShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([0])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)


class TestCLIPlay(TestAra):
    """ Tests for the ARA CLI play commands """
    def setUp(self):
        super(TestCLIPlay, self).setUp()

    def tearDown(self):
        super(TestCLIPlay, self).tearDown()

    def test_play_list_all(self):
        ctx = FakeRun()

        cmd = ara.cli.play.PlayList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--all'])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx.play['id'])

    def test_play_list_playbook(self):
        ctx = FakeRun()

        cmd = ara.cli.play.PlayList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([
            '--playbook',
            six.text_type(ctx.playbook['id'])
        ])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx.play['id'])

    def test_play_list_non_existing_playbook(self):
        cmd = ara.cli.play.PlayList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--playbook', six.text_type(9)])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_play_show(self):
        ctx = FakeRun()

        cmd = ara.cli.play.PlayShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([six.text_type(ctx.play['id'])])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx.play['id'])

    def test_play_show_non_existing(self):
        cmd = ara.cli.play.PlayShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([0])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)


class TestCLIPlaybook(TestAra):
    """ Tests for the ARA CLI playbook commands """
    def setUp(self):
        super(TestCLIPlaybook, self).setUp()
        self.playbook_api = PlaybookApi()
        self.file_api = FileApi()
        self.host_api = HostApi()
        self.play_api = PlayApi()
        self.task_api = TaskApi()
        self.result_api = ResultApi()

    def tearDown(self):
        super(TestCLIPlaybook, self).tearDown()

    def test_playbook_list(self):
        ctx = FakeRun()

        cmd = ara.cli.playbook.PlaybookList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx.playbook['id'])

    def test_playbook_list_complete(self):
        ctx = FakeRun()

        cmd = ara.cli.playbook.PlaybookList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--complete'])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx.playbook['id'])

    def test_playbook_list_complete_with_no_complete(self):
        FakeRun(completed=False)

        cmd = ara.cli.playbook.PlaybookList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--complete'])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_playbook_list_incomplete(self):
        ctx = FakeRun(completed=False)

        cmd = ara.cli.playbook.PlaybookList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--incomplete'])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx.playbook['id'])

    def test_playbook_list_incomplete_with_no_incomplete(self):
        FakeRun()

        cmd = ara.cli.playbook.PlaybookList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--incomplete'])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_playbook_show(self):
        ctx = FakeRun()

        cmd = ara.cli.playbook.PlaybookShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([six.text_type(ctx.playbook['id'])])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx.playbook['id'])

    def test_playbook_show_non_existing(self):
        cmd = ara.cli.playbook.PlaybookShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([0])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)

    def test_playbook_delete(self):
        # Run two playbook runs
        ctx = FakeRun()
        FakeRun()

        # Assert that we have two playbooks and that we have valid data for
        # the first playbook
        resp, playbooks = self.playbook_api.get()
        self.assertTrue(len(playbooks) == 2)

        # Validate that we have real data for this playbook
        resp, files = self.file_api.get(playbook_id=ctx.playbook['id'])
        self.assertNotEqual(len(files), 0)

        resp, hosts = self.host_api.get(playbook_id=ctx.playbook['id'])
        self.assertNotEqual(len(hosts), 0)

        resp, plays = self.play_api.get(playbook_id=ctx.playbook['id'])
        self.assertNotEqual(len(plays), 0)

        resp, tasks = self.task_api.get(playbook_id=ctx.playbook['id'])
        self.assertNotEqual(len(tasks), 0)

        resp, results = self.result_api.get(playbook_id=ctx.playbook['id'])
        self.assertNotEqual(len(results), 0)

        # Delete the playbook
        cmd = ara.cli.playbook.PlaybookDelete(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([six.text_type(ctx.playbook['id'])])
        cmd.take_action(args)

        # Assert that we only have one playbook left and that records have been
        # deleted
        resp, playbooks = self.playbook_api.get()
        self.assertTrue(len(playbooks) == 1)

        # Assert that we have no data for the first playbook
        resp, playbook = self.playbook_api.get(id=ctx.playbook['id'])
        self.assertEqual(resp.status_code, 404)

        # Validate that we nog longer have any data for this playbook
        resp, files = self.file_api.get(playbook_id=ctx.playbook['id'])
        self.assertEqual(resp.status_code, 404)

        resp, hosts = self.host_api.get(playbook_id=ctx.playbook['id'])
        self.assertEqual(resp.status_code, 404)

        resp, plays = self.play_api.get(playbook_id=ctx.playbook['id'])
        self.assertEqual(resp.status_code, 404)

        resp, tasks = self.task_api.get(playbook_id=ctx.playbook['id'])
        self.assertEqual(resp.status_code, 404)

        resp, results = self.result_api.get(playbook_id=ctx.playbook['id'])
        self.assertEqual(resp.status_code, 404)


class TestCLIResult(TestAra):
    """ Tests for the ARA CLI result commands """
    def setUp(self):
        super(TestCLIResult, self).setUp()
        self.client = ResultApi()

    def tearDown(self):
        super(TestCLIResult, self).tearDown()

    def test_result_list_all(self):
        ctx = FakeRun()

        cmd = ara.cli.result.ResultList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--all'])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx.playbook['results'][0]['id'])

    def test_result_list_playbook(self):
        ctx = FakeRun()

        cmd = ara.cli.result.ResultList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([
            '--playbook',
            six.text_type(ctx.playbook['id'])
        ])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx.playbook['results'][0]['id'])

    def test_result_list_non_existing_playbook(self):
        cmd = ara.cli.result.ResultList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--playbook', six.text_type(9)])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_result_list_play(self):
        ctx = FakeRun()

        cmd = ara.cli.result.ResultList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--play', six.text_type(ctx.play['id'])])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx.playbook['results'][0]['id'])

    def test_result_list_non_existing_play(self):
        cmd = ara.cli.result.ResultList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--play', six.text_type(9)])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_result_list_task(self):
        ctx = FakeRun()

        cmd = ara.cli.result.ResultList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--task', six.text_type(ctx.t_ok['id'])])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx.playbook['results'][0]['id'])

    def test_result_list_non_existing_task(self):
        cmd = ara.cli.result.ResultList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--task', six.text_type(9)])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_result_show(self):
        ctx = FakeRun()

        cmd = ara.cli.result.ResultShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([
            six.text_type(ctx.playbook['results'][0]['id'])
        ])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx.playbook['results'][0]['id'])

    def test_result_show_non_existing(self):
        cmd = ara.cli.result.ResultShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([0])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)

    def test_result_show_long(self):
        ctx = FakeRun()

        # Get result
        resp, result = self.client.get(id=ctx.playbook['results'][0]['id'])

        cmd = ara.cli.result.ResultShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([
            six.text_type(ctx.playbook['results'][0]['id']), '--long'
        ])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx.playbook['results'][0]['id'])
        self.assertEqual(res[1][-1], jsonutils.dumps(result['result'],
                                                     indent=4))

    def test_result_show_long_non_existing(self):
        cmd = ara.cli.result.ResultShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([0, '--long'])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)


class TestCLITask(TestAra):
    """ Tests for the ARA CLI task commands """
    def setUp(self):
        super(TestCLITask, self).setUp()

    def tearDown(self):
        super(TestCLITask, self).tearDown()

    def test_task_list_all(self):
        ctx = FakeRun()

        cmd = ara.cli.task.TaskList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--all'])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx.t_ok['id'])

    def test_task_list_play(self):
        ctx = FakeRun()

        cmd = ara.cli.task.TaskList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--play', six.text_type(ctx.play['id'])])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx.t_ok['id'])

    def test_task_list_non_existing_play(self):
        cmd = ara.cli.task.TaskList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--play', six.text_type(9)])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_task_list_playbook(self):
        ctx = FakeRun()

        cmd = ara.cli.task.TaskList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([
            '--playbook',
            six.text_type(ctx.playbook['id'])
        ])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx.t_ok['id'])

    def test_task_list_non_existing_playbook(self):
        cmd = ara.cli.task.TaskList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--playbook', six.text_type(9)])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_task_show(self):
        ctx = FakeRun()

        cmd = ara.cli.task.TaskShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([six.text_type(ctx.t_ok['id'])])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx.t_ok['id'])

    def test_task_show_non_existing(self):
        cmd = ara.cli.task.TaskShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([0])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)


class TestCLIGenerate(TestAra):
    """ Tests for the ARA CLI generate commands """
    def setUp(self):
        super(TestCLIGenerate, self).setUp()

    def tearDown(self):
        super(TestCLIGenerate, self).tearDown()

    def test_generate_junit(self):
        """ Roughly ensures the expected xml is generated properly """
        ctx = FakeRun()
        cmd = ara.cli.generate.GenerateJunit(None, None)
        parser = cmd.get_parser('test')

        junit_file = '{0}/junit.xml'.format(self.tmpdir)
        args = parser.parse_args([junit_file])
        cmd.take_action(args)

        self.assertTrue(os.path.exists(junit_file))

        tree = etree.parse(junit_file)
        self.assertEqual(tree.getroot().tag, "testsuites")
        self.assertEqual(tree.getroot()[0].tag, "testsuite")
        self.assertEqual(tree.getroot()[0][0].tag, "testcase")
        self.assertEqual(int(tree.getroot().get('tests')),
                         len(ctx.playbook['results']))
        self.assertEqual(int(tree.getroot().get('failures')),
                         2)

    def test_generate_junit_for_playbook(self):
        """ Roughly ensures the expected xml is generated properly """
        # Record two separate playbooks
        ctx = FakeRun()
        FakeRun()
        cmd = ara.cli.generate.GenerateJunit(None, None)
        parser = cmd.get_parser('test')

        junit_file = "{0}/junit-playbook.xml".format(self.tmpdir)
        args = parser.parse_args([
            junit_file,
            '--playbook',
            six.text_type(ctx.playbook['id'])
        ])
        cmd.take_action(args)

        self.assertTrue(os.path.exists(junit_file))

        tree = etree.parse(junit_file)
        self.assertEqual(tree.getroot().tag, "testsuites")
        self.assertEqual(tree.getroot()[0].tag, "testsuite")
        self.assertEqual(tree.getroot()[0][0].tag, "testcase")
        self.assertEqual(int(tree.getroot().get('tests')),
                         len(ctx.playbook['results']))

    def test_generate_subunit(self):
        """ Roughly ensures the expected subunit is generated properly """
        ctx = FakeRun()
        cmd = ara.cli.generate.GenerateSubunit(None, None)
        parser = cmd.get_parser('test')

        subunit_file = os.path.join(self.tmpdir, 'test.subunit')
        subunit_dir = os.path.join(self.tmpdir, 'subunit_dir')
        args = parser.parse_args([subunit_file])
        cmd.take_action(args)

        self.assertTrue(os.path.exists(subunit_file))
        # Dump the subunit binary stream to some files we can read and assert
        with open(subunit_file, 'r') as f:
            to_disk(['-d', subunit_dir], stdin=f)

        # Get *.json files, load them and test them
        data = []
        testfiles = glob("%s/%s" % (subunit_dir, '*/*.json'))
        for testfile in testfiles:
            with open(testfile, 'rb') as f:
                data.append(jsonutils.load(f))

        keys = ['status', 'tags', 'stop', 'start', 'details', 'id']
        for result in data:
            # Test that we have the expected keys, no more, no less
            for key in keys:
                self.assertTrue(key in result.keys())
            for key in result.keys():
                self.assertTrue(key in keys)

        # Get non-json files, load them and test them
        data = []
        testfiles = [fn for fn in glob("%s/%s" % (subunit_dir, '*/*'))
                     if not os.path.basename(fn).endswith('json')]
        for testfile in testfiles:
            with open(testfile, 'rb') as f:
                data.append(jsonutils.load(f))

        keys = ['host', 'playbook_id', 'playbook_path', 'play_name',
                'task_action', 'task_action_lineno', 'task_id', 'task_name',
                'task_path']
        for result in data:
            # Test that we have the expected keys, no more, no less
            for key in keys:
                self.assertTrue(key in result.keys())
            for key in result.keys():
                self.assertTrue(key in keys)

            # Test that we have matching data for playbook records
            self.assertEqual(ctx.playbook['id'], result['playbook_id'])
            self.assertEqual(ctx.playbook['path'], result['playbook_path'])

            # Test that we have matching data for task records
            resp, task = TaskApi().get(id=result['task_id'])
            self.assertEqual(task['id'], result['task_id'])
            self.assertEqual(task['action'], result['task_action'])
            self.assertEqual(task['lineno'], result['task_action_lineno'])
            self.assertEqual(task['name'], result['task_name'])
