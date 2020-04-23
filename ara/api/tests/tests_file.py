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

import datetime

from rest_framework.test import APITestCase

from ara.api import models, serializers
from ara.api.tests import factories, utils


class FileTestCase(APITestCase):
    def test_file_factory(self):
        file_content = factories.FileContentFactory()
        file = factories.FileFactory(path="/path/playbook.yml", content=file_content)
        self.assertEqual(file.path, "/path/playbook.yml")
        self.assertEqual(file.content.sha1, file_content.sha1)

    def test_file_serializer(self):
        playbook = factories.PlaybookFactory()
        serializer = serializers.FileSerializer(
            data={"path": "/path/playbook.yml", "content": factories.FILE_CONTENTS, "playbook": playbook.id}
        )
        serializer.is_valid()
        file = serializer.save()
        file.refresh_from_db()
        self.assertEqual(file.content.sha1, utils.sha1(factories.FILE_CONTENTS))

    def test_create_file_with_same_content_create_only_one_file_content(self):
        playbook = factories.PlaybookFactory()
        serializer = serializers.FileSerializer(
            data={"path": "/path/1/playbook.yml", "content": factories.FILE_CONTENTS, "playbook": playbook.id}
        )
        serializer.is_valid()
        file_content = serializer.save()
        file_content.refresh_from_db()

        serializer2 = serializers.FileSerializer(
            data={"path": "/path/2/playbook.yml", "content": factories.FILE_CONTENTS, "playbook": playbook.id}
        )
        serializer2.is_valid()
        file_content = serializer2.save()
        file_content.refresh_from_db()

        self.assertEqual(2, models.File.objects.all().count())
        self.assertEqual(1, models.FileContent.objects.all().count())

    def test_create_file(self):
        self.assertEqual(0, models.File.objects.count())
        playbook = factories.PlaybookFactory()
        request = self.client.post(
            "/api/v1/files", {"path": "/path/playbook.yml", "content": factories.FILE_CONTENTS, "playbook": playbook.id}
        )
        self.assertEqual(201, request.status_code)
        self.assertEqual(1, models.File.objects.count())

    def test_post_same_file_for_a_playbook(self):
        playbook = factories.PlaybookFactory()
        self.assertEqual(0, models.File.objects.count())
        request = self.client.post(
            "/api/v1/files", {"path": "/path/playbook.yml", "content": factories.FILE_CONTENTS, "playbook": playbook.id}
        )
        self.assertEqual(201, request.status_code)
        self.assertEqual(1, models.File.objects.count())

        request = self.client.post(
            "/api/v1/files", {"path": "/path/playbook.yml", "content": factories.FILE_CONTENTS, "playbook": playbook.id}
        )
        self.assertEqual(201, request.status_code)
        self.assertEqual(1, models.File.objects.count())

    def test_get_no_files(self):
        request = self.client.get("/api/v1/files")
        self.assertEqual(0, len(request.data["results"]))

    def test_get_files(self):
        file = factories.FileFactory()
        request = self.client.get("/api/v1/files")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(file.path, request.data["results"][0]["path"])

    def test_get_file(self):
        file = factories.FileFactory()
        request = self.client.get("/api/v1/files/%s" % file.id)
        self.assertEqual(file.path, request.data["path"])
        self.assertEqual(file.content.sha1, request.data["sha1"])

    def test_update_file(self):
        playbook = factories.PlaybookFactory()
        file = factories.FileFactory(playbook=playbook)
        old_sha1 = file.content.sha1
        self.assertNotEqual("/path/new_playbook.yml", file.path)
        request = self.client.put(
            "/api/v1/files/%s" % file.id,
            {"path": "/path/new_playbook.yml", "content": "# playbook", "playbook": playbook.id},
        )
        self.assertEqual(200, request.status_code)
        file_updated = models.File.objects.get(id=file.id)
        self.assertEqual("/path/new_playbook.yml", file_updated.path)
        self.assertNotEqual(old_sha1, file_updated.content.sha1)

    def test_partial_update_file(self):
        file = factories.FileFactory()
        self.assertNotEqual("/path/new_playbook.yml", file.path)
        request = self.client.patch("/api/v1/files/%s" % file.id, {"path": "/path/new_playbook.yml"})
        self.assertEqual(200, request.status_code)
        file_updated = models.File.objects.get(id=file.id)
        self.assertEqual("/path/new_playbook.yml", file_updated.path)

    def test_delete_file(self):
        file = factories.FileFactory()
        self.assertEqual(1, models.File.objects.all().count())
        request = self.client.delete("/api/v1/files/%s" % file.id)
        self.assertEqual(204, request.status_code)
        self.assertEqual(0, models.File.objects.all().count())

    def test_get_file_by_date(self):
        file = factories.FileFactory()

        past = datetime.datetime.now() - datetime.timedelta(hours=12)
        negative_date_fields = ["created_before", "updated_before"]
        positive_date_fields = ["created_after", "updated_after"]

        # Expect no file when searching before it was created
        for field in negative_date_fields:
            request = self.client.get("/api/v1/files?%s=%s" % (field, past.isoformat()))
            self.assertEqual(request.data["count"], 0)

        # Expect a file when searching after it was created
        for field in positive_date_fields:
            request = self.client.get("/api/v1/files?%s=%s" % (field, past.isoformat()))
            self.assertEqual(request.data["count"], 1)
            self.assertEqual(request.data["results"][0]["id"], file.id)

    def test_get_file_order(self):
        first_file = factories.FileFactory(path="/root/file.yaml")
        second_file = factories.FileFactory(path="/root/some/path/file.yaml")

        # Ensure we have two objects
        request = self.client.get("/api/v1/files")
        self.assertEqual(2, len(request.data["results"]))

        order_fields = ["id", "created", "updated", "path"]
        # Ascending order
        for field in order_fields:
            request = self.client.get("/api/v1/files?order=%s" % field)
            self.assertEqual(request.data["results"][0]["id"], first_file.id)

        # Descending order
        for field in order_fields:
            request = self.client.get("/api/v1/files?order=-%s" % field)
            self.assertEqual(request.data["results"][0]["id"], second_file.id)

    def test_get_file_by_path(self):
        # Create two files with similar paths
        first_file = factories.FileFactory(path="/root/file.yaml")
        factories.FileFactory(path="/root/some/path/file.yaml")

        # Exact search should match one
        request = self.client.get("/api/v1/files?path=/root/file.yaml")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(first_file.path, request.data["results"][0]["path"])

        # Partial match should match both files
        request = self.client.get("/api/v1/files?path=file.yaml")
        self.assertEqual(2, len(request.data["results"]))
