import datetime
from django.utils import timezone
from rest_framework.test import APITestCase

from ara.api import models, serializers
from ara.api.tests import factories


class PlaybookTestCase(APITestCase):
    def test_playbook_factory(self):
        playbook = factories.PlaybookFactory(ansible_version='2.4.0')
        self.assertEqual(playbook.ansible_version, '2.4.0')

    def test_playbook_serializer(self):
        serializer = serializers.PlaybookSerializer(data={
            'ansible_version': '2.4.0',
            'file': {
                'path': '/path/playbook.yml',
                'content': '# playbook'
            }
        })
        serializer.is_valid()
        playbook = serializer.save()
        playbook.refresh_from_db()
        self.assertEqual(playbook.ansible_version, '2.4.0')

    def test_playbook_serializer_compress_parameters(self):
        serializer = serializers.PlaybookSerializer(data={
            'ansible_version': '2.4.0',
            'file': {
                'path': '/path/playbook.yml',
                'content': '# playbook'
            },
            'parameters': {'foo': 'bar'}
        })
        serializer.is_valid()
        playbook = serializer.save()
        playbook.refresh_from_db()
        self.assertEqual(
            playbook.parameters,
            b'x\x9c\xabVJ\xcb\xcfW\xb2RPJJ,R\xaa\x05\x00 \x98\x04T'  # {'foo': 'bar'}
        )

    def test_playbook_serializer_decompress_parameters(self):
        playbook = factories.PlaybookFactory(
            parameters=b'x\x9c\xabVJ\xcb\xcfW\xb2RPJJ,R\xaa\x05\x00 \x98\x04T'  # {'foo': 'bar'}
        )
        serializer = serializers.PlaybookSerializer(instance=playbook)
        self.assertEqual(serializer.data['parameters'], {'foo': 'bar'})

    def test_get_no_playbooks(self):
        request = self.client.get('/api/v1/playbooks/')
        self.assertEqual(0, len(request.data['results']))

    def test_get_playbooks(self):
        playbook = factories.PlaybookFactory()
        request = self.client.get('/api/v1/playbooks/')
        self.assertEqual(1, len(request.data['results']))
        self.assertEqual(playbook.ansible_version, request.data['results'][0]['ansible_version'])

    def test_delete_playbook(self):
        playbook = factories.PlaybookFactory()
        self.assertEqual(1, models.Playbook.objects.all().count())
        request = self.client.delete('/api/v1/playbooks/%s/' % playbook.id)
        self.assertEqual(204, request.status_code)
        self.assertEqual(0, models.Playbook.objects.all().count())

    def test_create_playbook(self):
        self.assertEqual(0, models.Playbook.objects.count())
        request = self.client.post('/api/v1/playbooks/', {
            "ansible_version": "2.4.0",
            'file': {
                'path': '/path/playbook.yml',
                'content': '# playbook'
            }
        })
        self.assertEqual(201, request.status_code)
        self.assertEqual(1, models.Playbook.objects.count())

    def test_partial_update_playbook(self):
        playbook = factories.PlaybookFactory()
        self.assertNotEqual('2.3.0', playbook.ansible_version)
        request = self.client.patch('/api/v1/playbooks/%s/' % playbook.id, {
            "ansible_version": "2.3.0",
        })
        self.assertEqual(200, request.status_code)
        playbook_updated = models.Playbook.objects.get(id=playbook.id)
        self.assertEqual('2.3.0', playbook_updated.ansible_version)

    def test_get_playbook(self):
        playbook = factories.PlaybookFactory()
        request = self.client.get('/api/v1/playbooks/%s/' % playbook.id)
        self.assertEqual(playbook.ansible_version, request.data['ansible_version'])

    def test_get_playbook_duration(self):
        started = timezone.now()
        ended = started + datetime.timedelta(hours=1)
        playbook = factories.PlaybookFactory(started=started, ended=ended)
        request = self.client.get('/api/v1/playbooks/%s/' % playbook.id)
        self.assertEqual(request.data['duration'], datetime.timedelta(0, 3600))

    # TODO: Add tests for incrementally updating files
