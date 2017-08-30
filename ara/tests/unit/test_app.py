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

import pytest

from ara.tests.unit.fakes import FakeRun
from ara.tests.unit.common import TestAra


class TestApp(TestAra):
    """ Tests for the ARA web interface """
    def setUp(self):
        super(TestApp, self).setUp()

    def tearDown(self):
        super(TestApp, self).tearDown()

    def test_about_with_data(self):
        FakeRun()
        res = self.client.get('/about/')
        self.assertEqual(res.status_code, 200)

    def test_about_without_data(self):
        res = self.client.get('/about/')
        self.assertEqual(res.status_code, 200)

    def test_reports_without_data_at_root(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 302)

    def test_reports_without_data(self):
        res = self.client.get('/reports/')
        self.assertEqual(res.status_code, 302)

    def test_reports(self):
        FakeRun()
        res = self.client.get('/reports/')
        self.assertEqual(res.status_code, 200)

    def test_reports_with_incomplete(self):
        FakeRun(completed=False)
        res = self.client.get('/reports/')
        self.assertEqual(res.status_code, 200)

    def test_reports_with_override(self):
        ctx = FakeRun()
        self.app.config['ARA_PLAYBOOK_OVERRIDE'] = [ctx.playbook['id']]
        res = self.client.get('/reports/')
        self.assertEqual(res.status_code, 200)

    def test_reports_with_bad_override(self):
        FakeRun()
        self.app.config['ARA_PLAYBOOK_OVERRIDE'] = ['uuuu-iiii-dddd-0000']
        res = self.client.get('/reports/')
        self.assertEqual(res.status_code, 302)

    def test_reports_with_pagination(self):
        FakeRun()
        FakeRun()
        self.app.config['ARA_PLAYBOOK_PER_PAGE'] = 1
        res = self.client.get('/reports/')
        self.assertEqual(res.status_code, 200)

        res = self.client.get('/reports/list/1.html')
        self.assertEqual(res.status_code, 200)

        res = self.client.get('/reports/list/2.html')
        self.assertEqual(res.status_code, 200)

    def test_reports_single(self):
        ctx = FakeRun()
        res = self.client.get('/reports/{0}.html'.format(ctx.playbook['id']))
        self.assertEqual(res.status_code, 200)

    def test_reports_single_bad_playbook(self):
        FakeRun()
        res = self.client.get('/reports/0.html')
        self.assertEqual(res.status_code, 404)

    def test_report_ajax_parameters(self):
        ctx = FakeRun()
        pbid = ctx.playbook['id']
        res = self.client.get('/reports/ajax/parameters/{0}.txt'.format(pbid))
        self.assertEqual(res.status_code, 200)

    def test_report_ajax_no_parameters(self):
        FakeRun()
        res = self.client.get('/reports/ajax/parameters/0.txt')
        self.assertEqual(res.status_code, 404)

    def test_report_ajax_plays(self):
        ctx = FakeRun()
        pbid = ctx.playbook['id']
        res = self.client.get('/reports/ajax/plays/{0}.txt'.format(pbid))
        self.assertEqual(res.status_code, 200)

    def test_report_ajax_no_plays(self):
        FakeRun()
        res = self.client.get('/reports/ajax/plays/0.txt')
        self.assertEqual(res.status_code, 404)

    def test_report_ajax_records(self):
        ctx = FakeRun()
        pbid = ctx.playbook['id']
        res = self.client.get('/reports/ajax/records/{0}.txt'.format(pbid))
        self.assertEqual(res.status_code, 200)

    def test_report_ajax_no_records(self):
        FakeRun(record_task=False)
        res = self.client.get('/reports/ajax/records/0.txt')
        self.assertEqual(res.status_code, 404)

    def test_report_ajax_results(self):
        ctx = FakeRun()
        pbid = ctx.playbook['id']
        res = self.client.get('/reports/ajax/results/{0}.txt'.format(pbid))
        self.assertEqual(res.status_code, 200)

    def test_report_ajax_no_results(self):
        FakeRun()
        res = self.client.get('/reports/ajax/results/0.txt')
        self.assertEqual(res.status_code, 404)

    def test_report_ajax_hosts(self):
        ctx = FakeRun()
        pbid = ctx.playbook['id']
        res = self.client.get('/reports/ajax/hosts/{0}.txt'.format(pbid))
        self.assertEqual(res.status_code, 200)

    def test_report_ajax_no_hosts(self):
        FakeRun()
        res = self.client.get('/reports/ajax/hosts/0.txt')
        self.assertEqual(res.status_code, 404)

    def test_show_file(self):
        ctx = FakeRun()
        res = self.client.get('/file/{0}/'.format(
            ctx.playbook['files'][0]['id'])
        )
        self.assertEqual(res.status_code, 200)

    def test_show_file_index(self):
        FakeRun()
        res = self.client.get('/file/')
        self.assertEqual(res.status_code, 200)

    def test_show_host(self):
        ctx = FakeRun()
        res = self.client.get('/host/{}/'.format(
            ctx.playbook['hosts'][0]['id'])
        )
        self.assertEqual(res.status_code, 200)

    def test_show_host_index(self):
        FakeRun()
        res = self.client.get('/host/')
        self.assertEqual(res.status_code, 200)

    def test_show_host_missing(self):
        FakeRun()
        res = self.client.get('/host/foo/')
        self.assertEqual(res.status_code, 404)

    def test_show_host_exists_facts_missing(self):
        ctx = FakeRun(host_facts=False)
        res = self.client.get('/host/{}/'.format(
            ctx.playbook['hosts'][0]['id'])
        )
        self.assertEqual(res.status_code, 404)

    def test_show_host_missing_facts_missing(self):
        FakeRun()
        res = self.client.get('/host/foo/')
        self.assertEqual(res.status_code, 404)

    def test_show_result(self):
        ctx = FakeRun()
        res = self.client.get('/result/{}/'.format(
            ctx.t_ok['results'][0]['id'])
        )
        self.assertEqual(res.status_code, 200)

    def test_show_result_index(self):
        FakeRun()
        res = self.client.get('/result/')
        self.assertEqual(res.status_code, 200)

    def test_show_result_missing(self):
        FakeRun()
        res = self.client.get('/result/foo/')
        self.assertEqual(res.status_code, 404)

    @pytest.mark.incomplete
    def test_show_result_incomplete(self):
        ctx = FakeRun(completed=False)
        res = self.client.get('/result/{}/'.format(
            ctx.t_ok['results'][0]['id'])
        )
        self.assertEqual(res.status_code, 200)
