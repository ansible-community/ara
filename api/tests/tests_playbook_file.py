import datetime
from django.utils import timezone
from rest_framework.test import APITestCase

from api import models, serializers
from api.tests import factories


class PlaybookFileTestCase(APITestCase):
    def test_create_a_file_and_a_playbook_directly(self):
        self.assertEqual(0, models.Playbook.objects.all().count())
        self.assertEqual(0, models.File.objects.all().count())
        self.client.post('/api/v1/playbooks/', {
            'ansible_version': '2.4.0',
            'files': [{
                'path': '/tmp/playbook.yml',
                'content': '# playbook'
            }],
        })
        self.assertEqual(1, models.Playbook.objects.all().count())
        self.assertEqual(1, models.File.objects.all().count())
