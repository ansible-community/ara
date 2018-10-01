#  Copyright (c) 2018 Red Hat, Inc.
#
#  This file is part of ARA Records Ansible.
#
#  ARA is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  ARA is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with ARA.  If not, see <http://www.gnu.org/licenses/>.

from rest_framework.test import APITestCase

from ara.api import models
from ara.api.tests import factories


class PlaybookFileTestCase(APITestCase):
    def test_create_a_file_and_a_playbook_directly(self):
        self.assertEqual(0, models.Playbook.objects.all().count())
        self.assertEqual(0, models.File.objects.all().count())
        self.client.post(
            "/api/v1/playbooks",
            {
                "ansible_version": "2.4.0",
                "file": {"path": "/path/playbook.yml", "content": factories.FILE_CONTENTS},
                "files": [{"path": "/path/host", "content": "Another file"}],
            },
        )
        self.assertEqual(1, models.Playbook.objects.all().count())
        self.assertEqual(2, models.File.objects.all().count())

    def test_create_file_to_a_playbook(self):
        playbook = factories.PlaybookFactory()
        self.assertEqual(1, models.File.objects.all().count())
        self.client.post(
            "/api/v1/playbooks/%s/files" % playbook.id,
            {"path": "/path/playbook.yml", "content": factories.FILE_CONTENTS},
        )
        self.assertEqual(2, models.File.objects.all().count())
        self.assertEqual(1, models.FileContent.objects.all().count())

    def test_create_2_files_with_same_content(self):
        playbook = factories.PlaybookFactory()
        number_playbooks = models.File.objects.all().count()
        number_file_contents = models.FileContent.objects.all().count()
        content = "# %s" % factories.FILE_CONTENTS
        self.client.post(
            "/api/v1/playbooks/%s/files" % playbook.id, {"path": "/path/1/playbook.yml", "content": content}
        )
        self.client.post(
            "/api/v1/playbooks/%s/files" % playbook.id, {"path": "/path/2/playbook.yml", "content": content}
        )
        self.assertEqual(number_playbooks + 2, models.File.objects.all().count())
        self.assertEqual(number_file_contents + 1, models.FileContent.objects.all().count())
