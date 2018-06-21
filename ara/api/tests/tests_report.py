from rest_framework.test import APITestCase

from ara.api import models, serializers
from ara.api.tests import factories


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
            'description': 'description'
        })
        serializer.is_valid()
        report = serializer.save()
        report.refresh_from_db()
        self.assertEqual(report.description, b'x\x9cKI-N.\xca,(\xc9\xcc\xcf\x03\x00\x1b\x87\x04\xa5')  # 'description'

    def test_report_serializer_decompress_parameters(self):
        report = factories.ReportFactory(
            description=b'x\x9cKI-N.\xca,(\xc9\xcc\xcf\x03\x00\x1b\x87\x04\xa5'  # 'description'
        )
        serializer = serializers.ReportSerializer(instance=report)
        self.assertEqual(serializer.data['description'], 'description')

    def test_create_report(self):
        self.assertEqual(0, models.Report.objects.count())
        request = self.client.post('/api/v1/reports/', {
            'name': 'compress',
            'description': 'description'
        })
        self.assertEqual(201, request.status_code)
        self.assertEqual(1, models.Report.objects.count())

    def test_get_no_reports(self):
        request = self.client.get('/api/v1/reports/')
        self.assertEqual(0, len(request.data['results']))

    def test_get_reports(self):
        report = factories.ReportFactory()
        request = self.client.get('/api/v1/reports/')
        self.assertEqual(1, len(request.data['results']))
        self.assertEqual(report.name, request.data['results'][0]['name'])

    def test_get_report(self):
        report = factories.ReportFactory()
        request = self.client.get('/api/v1/reports/%s/' % report.id)
        self.assertEqual(report.name, request.data['name'])

    def test_partial_update_report(self):
        report = factories.ReportFactory()
        self.assertNotEqual('updated', report.name)
        request = self.client.patch('/api/v1/reports/%s/' % report.id, {
            'name': 'updated'
        })
        self.assertEqual(200, request.status_code)
        report_updated = models.Report.objects.get(id=report.id)
        self.assertEqual('updated', report_updated.name)

    def test_delete_report(self):
        report = factories.ReportFactory()
        self.assertEqual(1, models.Report.objects.all().count())
        request = self.client.delete('/api/v1/reports/%s/' % report.id)
        self.assertEqual(204, request.status_code)
        self.assertEqual(0, models.Report.objects.all().count())
