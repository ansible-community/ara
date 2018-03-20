from rest_framework.test import APITestCase

from api import models, serializers
from api.tests import factories


class FileTestCase(APITestCase):
    def test_file_factory(self):
        file_content = factories.FileContentFactory()
        file = factories.FileFactory(path='/tmp/playbook.yml', content=file_content)
        self.assertEqual(file.path, '/tmp/playbook.yml')
        self.assertEqual(file.content.sha1, file_content.sha1)

    def test_file_serializer(self):
        serializer = serializers.FileSerializer(data={
            'path': '/tmp/playbook.yml',
            'content': '# playbook'
        })
        serializer.is_valid()
        file = serializer.save()
        file.refresh_from_db()
        self.assertEqual(file.content.sha1, '1e58ead094c920fad631d2c22df34dc0314dab0c')

    def test_create_file_with_same_content_create_only_one_file_content(self):
        content = '# playbook'

        serializer = serializers.FileSerializer(data={
            'path': '/tmp/1/playbook.yml',
            'content': content
        })
        serializer.is_valid()
        file_content = serializer.save()
        file_content.refresh_from_db()

        serializer2 = serializers.FileSerializer(data={
            'path': '/tmp/2/playbook.yml',
            'content': content
        })
        serializer2.is_valid()
        file_content = serializer2.save()
        file_content.refresh_from_db()

        self.assertEqual(2, models.File.objects.all().count())
        self.assertEqual(1, models.FileContent.objects.all().count())

    def test_create_file(self):
        self.assertEqual(0, models.File.objects.count())
        request = self.client.post('/api/v1/files/', {
            'path': '/tmp/playbook.yml',
            'content': '# playbook'
        })
        self.assertEqual(201, request.status_code)
        self.assertEqual(1, models.File.objects.count())

    def test_get_no_files(self):
        request = self.client.get('/api/v1/files/')
        self.assertEqual(0, len(request.data['results']))

    def test_get_files(self):
        file = factories.FileFactory()
        request = self.client.get('/api/v1/files/')
        self.assertEqual(1, len(request.data['results']))
        self.assertEqual(file.path, request.data['results'][0]['path'])

    def test_get_file(self):
        file = factories.FileFactory()
        request = self.client.get('/api/v1/files/%s/' % file.id)
        self.assertEqual(file.path, request.data['path'])

    def test_update_file(self):
        file = factories.FileFactory()
        self.assertNotEqual('/tmp/new_playbook.yml', file.path)
        request = self.client.put('/api/v1/files/%s/' % file.id, {
            "path": "/tmp/new_playbook.yml",
            'content': '# playbook'
        })
        self.assertEqual(200, request.status_code)
        file_updated = models.File.objects.get(id=file.id)
        self.assertEqual('/tmp/new_playbook.yml', file_updated.path)

    def test_partial_update_file(self):
        file = factories.FileFactory()
        self.assertNotEqual('/tmp/new_playbook.yml', file.path)
        request = self.client.patch('/api/v1/files/%s/' % file.id, {
            "path": "/tmp/new_playbook.yml",
        })
        self.assertEqual(200, request.status_code)
        file_updated = models.File.objects.get(id=file.id)
        self.assertEqual('/tmp/new_playbook.yml', file_updated.path)

    def test_delete_file(self):
        file = factories.FileFactory()
        self.assertEqual(1, models.File.objects.all().count())
        request = self.client.delete('/api/v1/files/%s/' % file.id)
        self.assertEqual(204, request.status_code)
        self.assertEqual(0, models.File.objects.all().count())
