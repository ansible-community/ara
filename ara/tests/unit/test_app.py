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

import pytest

from ara.tests.unit.common import ansible_run
from ara.tests.unit.common import TestAra


class TestApp(TestAra):
    """ Tests for the ARA web interface """
    def setUp(self):
        super(TestApp, self).setUp()

    def tearDown(self):
        super(TestApp, self).tearDown()

    def test_overview(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)

    def test_list_playbook(self):
        ansible_run()
        res = self.client.get('/playbook/')
        self.assertEqual(res.status_code, 200)

    def test_list_playbook_incomplete(self):
        ansible_run(complete=False)
        res = self.client.get('/playbook/')
        self.assertEqual(res.status_code, 200)

    def test_show_playbook(self):
        ctx = ansible_run()
        res = self.client.get('/playbook/{}/'.format(
            ctx['playbook'].id))
        self.assertEqual(res.status_code, 200)

    def test_show_playbook_missing(self):
        ansible_run()
        res = self.client.get('/playbook/foo/')
        self.assertEqual(res.status_code, 404)

    @pytest.mark.incomplete
    def test_show_playbook_incomplete(self):
        ctx = ansible_run(complete=False)
        res = self.client.get('/playbook/{}/'.format(
            ctx['playbook'].id))
        self.assertEqual(res.status_code, 200)

    def test_show_playbook_results(self):
        ctx = ansible_run()
        res = self.client.get('/playbook/{}/results/'.format(
            ctx['playbook'].id))
        self.assertEqual(res.status_code, 200)

    def test_show_playbook_results_host(self):
        ctx = ansible_run()
        res = self.client.get('/playbook/{}/host/{}/'.format(
            ctx['playbook'].id,
            ctx['host'].name))
        self.assertEqual(res.status_code, 200)

    def test_show_playbook_results_host_status(self):
        ctx = ansible_run()
        res = self.client.get('/playbook/{}/host/{}/ok/'.format(
            ctx['playbook'].id,
            ctx['host'].name))
        self.assertEqual(res.status_code, 200)

    def test_show_playbook_results_play(self):
        ctx = ansible_run()
        res = self.client.get('/playbook/{}/play/{}/'.format(
            ctx['playbook'].id,
            ctx['play'].id))
        self.assertEqual(res.status_code, 200)

    def test_show_playbook_results_task(self):
        ctx = ansible_run()
        res = self.client.get('/playbook/{}/task/{}/'.format(
            ctx['playbook'].id,
            ctx['task'].id))
        self.assertEqual(res.status_code, 200)

    def test_show_playbook_results_missing(self):
        ansible_run()
        res = self.client.get('/playbook/foo/results/')
        self.assertEqual(res.status_code, 404)

    def test_show_host(self):
        ctx = ansible_run()
        res = self.client.get('/host/{}/'.format(ctx['host'].id))
        self.assertEqual(res.status_code, 200)

    def test_show_host_missing(self):
        ansible_run()
        res = self.client.get('/host/foo/')
        self.assertEqual(res.status_code, 404)

    def test_show_host_exists_facts_missing(self):
        ctx = ansible_run(gather_facts=False)
        res = self.client.get('/host/{}/'.format(ctx['host'].id))
        self.assertEqual(res.status_code, 404)

    def test_show_host_missing_facts_missing(self):
        ansible_run()
        res = self.client.get('/host/foo/')
        self.assertEqual(res.status_code, 404)

    @pytest.mark.incomplete
    def test_show_host_incomplete(self):
        ctx = ansible_run(complete=False)
        res = self.client.get('/host/{}/'.format(ctx['host'].id))
        self.assertEqual(res.status_code, 200)

    def test_show_result(self):
        ctx = ansible_run()
        res = self.client.get('/result/{}/'.format(
            ctx['result'].id))
        self.assertEqual(res.status_code, 200)

    def test_show_result_missing(self):
        ansible_run()
        res = self.client.get('/result/foo/')
        self.assertEqual(res.status_code, 404)

    @pytest.mark.incomplete
    def test_show_result_incomplete(self):
        ctx = ansible_run(complete=False)
        res = self.client.get('/result/{}/'.format(
            ctx['result'].id))
        self.assertEqual(res.status_code, 200)
