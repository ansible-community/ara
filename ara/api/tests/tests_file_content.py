from rest_framework.test import APITestCase

from ara.api.tests import factories


class FileContentTestCase(APITestCase):
    def test_file_content_factory(self):
        file_content = factories.FileContentFactory(sha1='413a2f16b8689267b7d0c2e10cdd19bf3e54208d')
        self.assertEqual(file_content.sha1, '413a2f16b8689267b7d0c2e10cdd19bf3e54208d')
