import time
from rest_framework.test import APITestCase

from api import models
from api.tests import factories


class PlaybookFileTestCase(APITestCase):
    def test_create_a_file_and_a_playbook_directly(self):
        self.assertEqual(0, models.Playbook.objects.all().count())
        self.assertEqual(0, models.File.objects.all().count())
        self.client.post('/api/v1/playbooks/', {
            'ansible_version': '2.4.0',
            'file': {
                'path': '/tmp/playbook.yml',
                'content': '# playbook'
            },
            'files': [{
                'path': '/tmp/host',
                'content': '# host'
            }],
        })
        self.assertEqual(1, models.Playbook.objects.all().count())
        self.assertEqual(2, models.File.objects.all().count())

    def test_create_file_to_a_playbook(self):
        playbook = factories.PlaybookFactory()
        self.assertEqual(1, models.File.objects.all().count())
        self.client.post('/api/v1/playbooks/%s/files/' % playbook.id, {
            'path': '/tmp/playbook.yml',
            'content': '# playbook'
        })
        self.assertEqual(2, models.File.objects.all().count())
        self.assertEqual(1, models.FileContent.objects.all().count())

    def test_create_2_files_with_same_content(self):
        playbook = factories.PlaybookFactory()
        number_playbooks = models.File.objects.all().count()
        number_file_contents = models.FileContent.objects.all().count()
        content = '# playbook %s' % time.time()
        self.client.post('/api/v1/playbooks/%s/files/' % playbook.id, {
            'path': '/tmp/1/playbook.yml',
            'content': content
        })
        self.client.post('/api/v1/playbooks/%s/files/' % playbook.id, {
            'path': '/tmp/2/playbook.yml',
            'content': content
        })
        self.assertEqual(number_playbooks + 2, models.File.objects.all().count())
        self.assertEqual(number_file_contents + 1, models.FileContent.objects.all().count())
