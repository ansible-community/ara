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

from django.utils import timezone
from rest_framework.test import APITestCase

from ara.api import models, serializers
from ara.api.tests import factories, utils


class PlaybookTestCase(APITestCase):
    def test_playbook_factory(self):
        playbook = factories.PlaybookFactory(ansible_version="2.4.0")
        self.assertEqual(playbook.ansible_version, "2.4.0")

    def test_playbook_serializer(self):
        serializer = serializers.PlaybookSerializer(
            data={"name": "serializer-playbook", "ansible_version": "2.4.0", "path": "/path/playbook.yml"}
        )
        serializer.is_valid()
        playbook = serializer.save()
        playbook.refresh_from_db()
        self.assertEqual(playbook.name, "serializer-playbook")
        self.assertEqual(playbook.ansible_version, "2.4.0")
        self.assertEqual(playbook.status, "unknown")

    def test_playbook_serializer_compress_arguments(self):
        serializer = serializers.PlaybookSerializer(
            data={"ansible_version": "2.4.0", "path": "/path/playbook.yml", "arguments": factories.PLAYBOOK_ARGUMENTS}
        )
        serializer.is_valid()
        playbook = serializer.save()
        playbook.refresh_from_db()
        self.assertEqual(playbook.arguments, utils.compressed_obj(factories.PLAYBOOK_ARGUMENTS))

    def test_playbook_serializer_decompress_arguments(self):
        playbook = factories.PlaybookFactory(arguments=utils.compressed_obj(factories.PLAYBOOK_ARGUMENTS))
        serializer = serializers.PlaybookSerializer(instance=playbook)
        self.assertEqual(serializer.data["arguments"], factories.PLAYBOOK_ARGUMENTS)

    def test_get_no_playbooks(self):
        request = self.client.get("/api/v1/playbooks")
        self.assertEqual(0, len(request.data["results"]))

    def test_get_playbooks(self):
        expected_playbook = factories.PlaybookFactory()
        request = self.client.get("/api/v1/playbooks")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(1, request.data["count"])
        playbook = request.data["results"][0]
        self.assertEqual(playbook["ansible_version"], expected_playbook.ansible_version)

    def test_delete_playbook(self):
        playbook = factories.PlaybookFactory()
        self.assertEqual(1, models.Playbook.objects.all().count())
        request = self.client.delete("/api/v1/playbooks/%s" % playbook.id)
        self.assertEqual(204, request.status_code)
        self.assertEqual(0, models.Playbook.objects.all().count())

    def test_create_playbook(self):
        self.assertEqual(0, models.Playbook.objects.count())
        request = self.client.post(
            "/api/v1/playbooks", {"ansible_version": "2.4.0", "status": "running", "path": "/path/playbook.yml"}
        )
        self.assertEqual(201, request.status_code)
        self.assertEqual(1, models.Playbook.objects.count())
        self.assertEqual(request.data["status"], "running")

    def test_partial_update_playbook(self):
        playbook = factories.PlaybookFactory()
        self.assertNotEqual("completed", playbook.status)
        request = self.client.patch("/api/v1/playbooks/%s" % playbook.id, {"status": "completed"})
        self.assertEqual(200, request.status_code)
        playbook_updated = models.Playbook.objects.get(id=playbook.id)
        self.assertEqual("completed", playbook_updated.status)

    def test_update_wrong_playbook_status(self):
        playbook = factories.PlaybookFactory()
        self.assertNotEqual("wrong", playbook.status)
        request = self.client.patch("/api/v1/playbooks/%s" % playbook.id, {"status": "wrong"})
        self.assertEqual(400, request.status_code)
        playbook_updated = models.Playbook.objects.get(id=playbook.id)
        self.assertNotEqual("wrong", playbook_updated.status)

    def test_get_playbook(self):
        playbook = factories.PlaybookFactory()
        request = self.client.get("/api/v1/playbooks/%s" % playbook.id)
        self.assertEqual(playbook.ansible_version, request.data["ansible_version"])

    def test_get_playbook_by_name(self):
        playbook = factories.PlaybookFactory(name="playbook1")
        factories.PlaybookFactory(name="playbook2")
        request = self.client.get("/api/v1/playbooks?name=playbook1")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(playbook.name, request.data["results"][0]["name"])

    def test_get_playbook_by_status(self):
        playbook = factories.PlaybookFactory(status="failed")
        factories.PlaybookFactory(status="completed")
        request = self.client.get("/api/v1/playbooks?status=failed")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(playbook.status, request.data["results"][0]["status"])

    def test_get_playbook_duration(self):
        started = timezone.now()
        ended = started + datetime.timedelta(hours=1)
        playbook = factories.PlaybookFactory(started=started, ended=ended)
        request = self.client.get("/api/v1/playbooks/%s" % playbook.id)
        self.assertEqual(request.data["duration"], datetime.timedelta(0, 3600))

    # TODO: Add tests for incrementally updating files
