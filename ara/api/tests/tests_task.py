import datetime
from django.utils import timezone
from rest_framework.test import APITestCase

from ara.api import models, serializers
from ara.api.tests import factories


class TaskTestCase(APITestCase):
    def test_task_factory(self):
        task = factories.TaskFactory(name='factory')
        self.assertEqual(task.name, 'factory')

    def test_task_serializer(self):
        play = factories.PlayFactory()
        file = factories.FileFactory()
        serializer = serializers.TaskSerializer(data={
            'name': 'serializer',
            'action': 'test',
            'lineno': 2,
            'completed': True,
            'handler': False,
            'play': play.id,
            'file': file.id
        })
        serializer.is_valid()
        task = serializer.save()
        task.refresh_from_db()
        self.assertEqual(task.name, 'serializer')

    def test_task_serializer_compress_tags(self):
        play = factories.PlayFactory()
        file = factories.FileFactory()
        serializer = serializers.TaskSerializer(data={
            'name': 'compress',
            'action': 'test',
            'lineno': 2,
            'completed': True,
            'handler': False,
            'play': play.id,
            'file': file.id,
            'tags': ['foo', 'bar']
        })
        serializer.is_valid()
        task = serializer.save()
        task.refresh_from_db()
        self.assertEqual(task.tags, b'x\x9c\x8bVJ\xcb\xcfW\xd2QPJJ,R\x8a\x05\x00\x1eH\x04\x06')  # ['foo', 'bar']

    def test_task_serializer_decompress_tags(self):
        task = factories.TaskFactory(tags=b'x\x9c\x8bVJ\xcb\xcfW\xd2QPJJ,R\x8a\x05\x00\x1eH\x04\x06')  # ['foo', 'bar']
        serializer = serializers.TaskSerializer(instance=task)
        self.assertEqual(serializer.data['tags'], ['foo', 'bar'])

    def test_get_no_tasks(self):
        request = self.client.get('/api/v1/tasks/')
        self.assertEqual(0, len(request.data['results']))

    def test_get_tasks(self):
        task = factories.TaskFactory()
        request = self.client.get('/api/v1/tasks/')
        self.assertEqual(1, len(request.data['results']))
        self.assertEqual(task.name, request.data['results'][0]['name'])

    def test_delete_task(self):
        task = factories.TaskFactory()
        self.assertEqual(1, models.Task.objects.all().count())
        request = self.client.delete('/api/v1/tasks/%s/' % task.id)
        self.assertEqual(204, request.status_code)
        self.assertEqual(0, models.Task.objects.all().count())

    def test_create_task(self):
        play = factories.PlayFactory()
        file = factories.FileFactory()
        self.assertEqual(0, models.Task.objects.count())
        request = self.client.post('/api/v1/tasks/', {
            'name': 'create',
            'action': 'test',
            'lineno': 2,
            'handler': False,
            'completed': True,
            'play': play.id,
            'file': file.id
        })
        self.assertEqual(201, request.status_code)
        self.assertEqual(1, models.Task.objects.count())

    def test_partial_update_task(self):
        task = factories.TaskFactory()
        self.assertNotEqual('update', task.name)
        request = self.client.patch('/api/v1/tasks/%s/' % task.id, {
            'name': 'update'
        })
        self.assertEqual(200, request.status_code)
        task_updated = models.Task.objects.get(id=task.id)
        self.assertEqual('update', task_updated.name)

    def test_get_task(self):
        task = factories.TaskFactory()
        request = self.client.get('/api/v1/tasks/%s/' % task.id)
        self.assertEqual(task.name, request.data['name'])

    def test_get_task_duration(self):
        started = timezone.now()
        ended = started + datetime.timedelta(hours=1)
        task = factories.TaskFactory(started=started, ended=ended)
        request = self.client.get('/api/v1/tasks/%s/' % task.id)
        self.assertEqual(request.data['duration'], datetime.timedelta(0, 3600))
