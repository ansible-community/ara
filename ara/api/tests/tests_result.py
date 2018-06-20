from rest_framework.test import APITestCase

from ara.api import models, serializers
from ara.api.tests import factories


class ResultTestCase(APITestCase):
    def test_result_factory(self):
        result = factories.ResultFactory(status='failed')
        self.assertEqual(result.status, 'failed')

    def test_result_serializer(self):
        host = factories.HostFactory()
        task = factories.TaskFactory()
        serializer = serializers.ResultSerializer(data={
            'status': 'skipped',
            'host': host.id,
            'task': task.id
        })
        serializer.is_valid()
        result = serializer.save()
        result.refresh_from_db()
        self.assertEqual(result.status, 'skipped')
        self.assertEqual(result.host.id, host.id)
        self.assertEqual(result.task.id, task.id)

    def test_result_serializer_compress_content(self):
        host = factories.HostFactory()
        task = factories.TaskFactory()
        serializer = serializers.ResultSerializer(data={
            'host': host.id,
            'task': task.id,
            'content': {'foo': 'bar'}
        })
        serializer.is_valid()
        result = serializer.save()
        result.refresh_from_db()
        self.assertEqual(
            result.content, b'x\x9c\xabVJ\xcb\xcfW\xb2RPJJ,R\xaa\x05\x00 \x98\x04T'  # {'foo': 'bar'}
        )

    def test_result_serializer_decompress_content(self):
        result = factories.ResultFactory(
            content=b'x\x9c\xabVJ\xcb\xcfW\xb2RPJJ,R\xaa\x05\x00 \x98\x04T'  # {'foo': 'bar'}
        )
        serializer = serializers.ResultSerializer(instance=result)
        self.assertEqual(serializer.data['content'], {'foo': 'bar'})

    def test_get_no_results(self):
        request = self.client.get('/api/v1/results/')
        self.assertEqual(0, len(request.data['results']))

    def test_get_results(self):
        result = factories.ResultFactory()
        request = self.client.get('/api/v1/results/')
        self.assertEqual(1, len(request.data['results']))
        self.assertEqual(result.status, request.data['results'][0]['status'])

    def test_delete_result(self):
        result = factories.ResultFactory()
        self.assertEqual(1, models.Result.objects.all().count())
        request = self.client.delete('/api/v1/results/%s/' % result.id)
        self.assertEqual(204, request.status_code)
        self.assertEqual(0, models.Result.objects.all().count())

    def test_create_result(self):
        host = factories.HostFactory()
        task = factories.TaskFactory()
        self.assertEqual(0, models.Result.objects.count())
        request = self.client.post('/api/v1/results/', {
            'status': 'ok',
            'host': host.id,
            'task': task.id,
            'content': {'foo': 'bar'}
        })
        self.assertEqual(201, request.status_code)
        self.assertEqual(1, models.Result.objects.count())

    def test_partial_update_result(self):
        result = factories.ResultFactory()
        self.assertNotEqual('unreachable', result.status)
        request = self.client.patch('/api/v1/results/%s/' % result.id, {
            'status': 'unreachable'
        })
        self.assertEqual(200, request.status_code)
        result_updated = models.Result.objects.get(id=result.id)
        self.assertEqual('unreachable', result_updated.status)

    def test_get_result(self):
        result = factories.ResultFactory()
        request = self.client.get('/api/v1/results/%s/' % result.id)
        self.assertEqual(result.status, request.data['status'])
