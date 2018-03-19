from rest_framework.test import APITestCase

from api import serializers
from api.tests import factories


class FileContentTestCase(APITestCase):
    def test_file_content_factory(self):
        file_content = factories.FileContentFactory(sha1='413a2f16b8689267b7d0c2e10cdd19bf3e54208d')
        self.assertEqual(file_content.sha1, '413a2f16b8689267b7d0c2e10cdd19bf3e54208d')

    def test_file_content_serializer_compress_contents(self):
        serializer = serializers.FileContentSerializer(data={'contents': '# playbook'})
        serializer.is_valid()
        file_content = serializer.save()
        file_content.refresh_from_db()
        self.assertEqual(file_content.sha1, '1e58ead094c920fad631d2c22df34dc0314dab0c')
        self.assertEqual(file_content.contents, b'x\x9cSV(\xc8I\xacL\xca\xcf\xcf\x06\x00\x11\xbd\x03\xa5')

    def test_file_content_serializer_decompress_contents(self):
        file_content = factories.FileContentFactory(contents=b'x\x9cSV(\xc8I\xacL\xca\xcf\xcf\x06\x00\x11\xbd\x03\xa5')
        serializer = serializers.FileContentSerializer(instance=file_content)
        self.assertEqual(serializer.data['contents'], '# playbook')
