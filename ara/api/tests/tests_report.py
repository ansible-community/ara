#  Copyright (c) 2018 Red Hat, Inc.
#
#  This file is part of ARA Records Ansible.
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

from rest_framework.test import APITestCase

from ara.api import models, serializers
from ara.api.tests import factories
from ara.api.tests import utils


class ReportTestCase(APITestCase):
    def test_report_factory(self):
        report = factories.ReportFactory(name='factory')
        self.assertEqual(report.name, 'factory')

    def test_report_serializer(self):
        serializer = serializers.ReportSerializer(data={
            'name': 'serializer',
        })
        serializer.is_valid()
        report = serializer.save()
        report.refresh_from_db()
        self.assertEqual(report.name, 'serializer')

    def test_report_serializer_compress_description(self):
        serializer = serializers.ReportSerializer(data={
            'name': 'compress',
            'description': factories.REPORT_DESCRIPTION
        })
        serializer.is_valid()
        report = serializer.save()
        report.refresh_from_db()
        self.assertEqual(report.description, utils.compressed_str(factories.REPORT_DESCRIPTION))

    def test_report_serializer_decompress_description(self):
        report = factories.ReportFactory(
            description=utils.compressed_str(factories.REPORT_DESCRIPTION)
        )
        serializer = serializers.ReportSerializer(instance=report)
        self.assertEqual(serializer.data['description'], factories.REPORT_DESCRIPTION)

    def test_create_report(self):
        self.assertEqual(0, models.Report.objects.count())
        request = self.client.post('/api/v1/reports', {
            'name': 'compress',
            'description': factories.REPORT_DESCRIPTION
        })
        self.assertEqual(201, request.status_code)
        self.assertEqual(1, models.Report.objects.count())

    def test_get_no_reports(self):
        request = self.client.get('/api/v1/reports')
        self.assertEqual(0, len(request.data['results']))

    def test_get_reports(self):
        report = factories.ReportFactory()
        request = self.client.get('/api/v1/reports')
        self.assertEqual(1, len(request.data['results']))
        self.assertEqual(report.name, request.data['results'][0]['name'])

    def test_get_report(self):
        report = factories.ReportFactory()
        request = self.client.get('/api/v1/reports/%s' % report.id)
        self.assertEqual(report.name, request.data['name'])

    def test_partial_update_report(self):
        report = factories.ReportFactory()
        self.assertNotEqual('updated', report.name)
        request = self.client.patch('/api/v1/reports/%s' % report.id, {
            'name': 'updated'
        })
        self.assertEqual(200, request.status_code)
        report_updated = models.Report.objects.get(id=report.id)
        self.assertEqual('updated', report_updated.name)

    def test_delete_report(self):
        report = factories.ReportFactory()
        self.assertEqual(1, models.Report.objects.all().count())
        request = self.client.delete('/api/v1/reports/%s' % report.id)
        self.assertEqual(204, request.status_code)
        self.assertEqual(0, models.Report.objects.all().count())
