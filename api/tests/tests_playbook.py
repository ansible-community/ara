import datetime
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request

from api import models, serializers
from api.tests import factories


class PlaybookTestCase(APITestCase):
    def test_playbook_factory(self):
        playbook = factories.PlaybookFactory(path='/tmp/playbook.yml', ansible_version='2.4.0')
        self.assertEqual(playbook.path, '/tmp/playbook.yml')
        self.assertEqual(playbook.ansible_version, '2.4.0')

    def test_playbook_serializer(self):
        serializer = serializers.PlaybookSerializer(data={
            'path': '/tmp/playbook.yml',
            'ansible_version': '2.4.0'
        })
        serializer.is_valid()
        playbook = serializer.save()
        playbook.refresh_from_db()
        self.assertEqual(playbook.path, '/tmp/playbook.yml')
        self.assertEqual(playbook.ansible_version, '2.4.0')

    def test_playbook_serializer_compress_parameters(self):
        serializer = serializers.PlaybookSerializer(data={
            'path': '/tmp/playbook.yml',
            'ansible_version': '2.4.0',
            'parameters': {'foo': 'bar'}
        })
        serializer.is_valid()
        playbook = serializer.save()
        playbook.refresh_from_db()
        self.assertEqual(playbook.parameters, b'x\x9c\xabVJ\xcb\xcfW\xb2RPJJ,R\xaa\x05\x00 \x98\x04T')

    def test_playbook_serializer_decompress_parameters(self):
        playbook = factories.PlaybookFactory(parameters=b'x\x9c\xabVJ\xcb\xcfW\xb2RPJJ,R\xaa\x05\x00 \x98\x04T')
        serializer = serializers.PlaybookSerializer(instance=playbook, context={
            'request': Request(APIRequestFactory().get('/')),
        })
        self.assertEqual(serializer.data['parameters'], {'foo': 'bar'})

    def test_get_no_playbooks(self):
        request = self.client.get('/api/v1/playbooks/')
        self.assertEqual(0, len(request.data['results']))

    def test_get_playbooks(self):
        playbook = factories.PlaybookFactory()
        request = self.client.get('/api/v1/playbooks/')
        self.assertEqual(1, len(request.data['results']))
        self.assertEqual(playbook.path, request.data['results'][0]['path'])

    def test_delete_playbook(self):
        playbook = factories.PlaybookFactory()
        self.assertEqual(1, models.Playbook.objects.all().count())
        request = self.client.delete('/api/v1/playbooks/%s/' % playbook.id)
        self.assertEqual(204, request.status_code)
        self.assertEqual(0, models.Playbook.objects.all().count())

    def test_create_playbook(self):
        self.assertEqual(0, models.Playbook.objects.count())
        playbook = {
            "path": "/tmp/playbook.yml",
            "ansible_version": "2.4.0",
        }
        request = self.client.post('/api/v1/playbooks/', playbook)
        self.assertEqual(201, request.status_code)
        self.assertEqual(1, models.Playbook.objects.count())

    def test_update_playbook(self):
        playbook = factories.PlaybookFactory()
        self.assertNotEqual('/home/ara/playbook.yml', playbook.path)
        new_playbook = {
            "path": "/home/ara/playbook.yml",
            "ansible_version": "2.4.0",
        }
        request = self.client.put('/api/v1/playbooks/%s/' % playbook.id, new_playbook)
        self.assertEqual(200, request.status_code)
        playbook_updated = models.Playbook.objects.get(id=playbook.id)
        self.assertEqual('/home/ara/playbook.yml', playbook_updated.path)

    def test_get_playbook(self):
        playbook = factories.PlaybookFactory()
        request = self.client.get('/api/v1/playbooks/%s/' % playbook.id)
        self.assertEqual(playbook.path, request.data['path'])
        self.assertEqual(playbook.ansible_version, request.data['ansible_version'])

    def test_get_playbook_duration(self):
        started = timezone.now()
        ended = started + datetime.timedelta(hours=1)
        playbook = factories.PlaybookFactory(started=started, ended=ended)
        request = self.client.get('/api/v1/playbooks/%s/' % playbook.id)
        self.assertEqual(request.data['duration'], datetime.timedelta(0, 3600))
