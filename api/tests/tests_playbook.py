from rest_framework.test import APITestCase

from api import models
from api.tests import factories


class PlaybookTestCase(APITestCase):
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
