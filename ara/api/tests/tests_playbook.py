# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import datetime

from django.utils import timezone
from django.utils.dateparse import parse_duration
from rest_framework.test import APITestCase

from ara.api import models, serializers
from ara.api.tests import factories, utils
from ara.setup import ara_version as ARA_VERSION


class PlaybookTestCase(APITestCase):
    def test_playbook_factory(self):
        playbook = factories.PlaybookFactory(ansible_version="2.4.0")
        self.assertEqual(playbook.ansible_version, "2.4.0")

    def test_playbook_serializer(self):
        serializer = serializers.PlaybookSerializer(
            data={
                "controller": "serializer",
                "name": "serializer-playbook",
                "user": "ara-user",
                "ansible_version": "2.4.0",
                "client_version": "0.16.7",
                "path": "/path/playbook.yml",
            }
        )
        serializer.is_valid()
        playbook = serializer.save()
        playbook.refresh_from_db()
        self.assertEqual(playbook.controller, "serializer")
        self.assertEqual(playbook.name, "serializer-playbook")
        self.assertEqual(playbook.user, "ara-user")
        self.assertEqual(playbook.ansible_version, "2.4.0")
        self.assertEqual(playbook.client_version, "0.16.7")
        self.assertEqual(playbook.server_version, ARA_VERSION)
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

    def test_create_playbook_with_labels(self):
        self.assertEqual(0, models.Playbook.objects.count())
        labels = ["test-label", "another-test-label"]
        request = self.client.post(
            "/api/v1/playbooks",
            {"ansible_version": "2.4.0", "status": "running", "path": "/path/playbook.yml", "labels": labels},
        )
        self.assertEqual(201, request.status_code)
        self.assertEqual(1, models.Playbook.objects.count())
        self.assertEqual(request.data["status"], "running")
        self.assertEqual(sorted(label["name"] for label in request.data["labels"]), sorted(labels))

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

    def test_expired_playbook(self):
        playbook = factories.PlaybookFactory(status="running")
        self.assertEqual("running", playbook.status)

        request = self.client.patch("/api/v1/playbooks/%s" % playbook.id, {"status": "expired"})
        self.assertEqual(200, request.status_code)
        playbook_updated = models.Playbook.objects.get(id=playbook.id)
        self.assertEqual("expired", playbook_updated.status)

    def test_get_playbook(self):
        playbook = factories.PlaybookFactory()
        request = self.client.get("/api/v1/playbooks/%s" % playbook.id)
        self.assertEqual(playbook.ansible_version, request.data["ansible_version"])

    def test_get_playbook_by_controller(self):
        playbook = factories.PlaybookFactory(name="playbook1", controller="controller-one")
        factories.PlaybookFactory(name="playbook2", controller="controller-two")

        # Test exact match
        request = self.client.get("/api/v1/playbooks?controller=controller-one")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(playbook.name, request.data["results"][0]["name"])
        self.assertEqual(playbook.controller, request.data["results"][0]["controller"])

        # Test partial match
        request = self.client.get("/api/v1/playbooks?controller=controller")
        self.assertEqual(len(request.data["results"]), 2)

    def test_get_playbook_by_user(self):
        playbook = factories.PlaybookFactory(name="playbook1", user="foobar")
        factories.PlaybookFactory(name="playbook2", user="foobaz")

        # Test exact match
        request = self.client.get("/api/v1/playbooks?user=foobar")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(playbook.name, request.data["results"][0]["name"])
        self.assertEqual(playbook.user, request.data["results"][0]["user"])

        # Test partial match
        request = self.client.get("/api/v1/playbooks?user=foo")
        self.assertEqual(len(request.data["results"]), 2)

    def test_get_playbook_by_name(self):
        playbook = factories.PlaybookFactory(name="playbook1")
        factories.PlaybookFactory(name="playbook2")

        # Test exact match
        request = self.client.get("/api/v1/playbooks?name=playbook1")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(playbook.name, request.data["results"][0]["name"])

        # Test partial match
        request = self.client.get("/api/v1/playbooks?name=playbook")
        self.assertEqual(len(request.data["results"]), 2)

    def test_get_playbook_by_ansible_version(self):
        playbook = factories.PlaybookFactory(name="playbook1", ansible_version="2.9.1")
        factories.PlaybookFactory(name="playbook2", ansible_version="2.8.2")

        # Test exact match
        request = self.client.get("/api/v1/playbooks?ansible_version=2.9.1")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(playbook.name, request.data["results"][0]["name"])

        # Test partial match
        request = self.client.get("/api/v1/playbooks?ansible_version=2.9")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(playbook.name, request.data["results"][0]["name"])

    def test_get_playbook_by_client_version(self):
        playbook = factories.PlaybookFactory(name="playbook1", client_version="0.16.7")
        factories.PlaybookFactory(name="playbook2", client_version=ARA_VERSION)

        # Test exact match
        request = self.client.get("/api/v1/playbooks?client_version=0.16.7")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(playbook.name, request.data["results"][0]["name"])

        # Test partial match
        request = self.client.get("/api/v1/playbooks?client_version=0.16")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(playbook.name, request.data["results"][0]["name"])

    def test_get_playbook_by_server_version(self):
        playbook = factories.PlaybookFactory(name="playbook1", server_version="7.16.0")
        factories.PlaybookFactory(name="playbook2", server_version=ARA_VERSION)

        # Test exact match
        request = self.client.get("/api/v1/playbooks?server_version=7.16.0")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(playbook.name, request.data["results"][0]["name"])

        # Test partial match
        request = self.client.get("/api/v1/playbooks?server_version=7.16")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(playbook.name, request.data["results"][0]["name"])

    def test_get_playbook_by_python_version(self):
        playbook = factories.PlaybookFactory(name="playbook1", python_version="3.2.1")
        factories.PlaybookFactory(name="playbook2", python_version="4.5.6")

        # Test exact match
        request = self.client.get("/api/v1/playbooks?python_version=3.2.1")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(playbook.name, request.data["results"][0]["name"])

        # Test partial match
        request = self.client.get("/api/v1/playbooks?python_version=3.2")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(playbook.name, request.data["results"][0]["name"])

    def test_get_playbook_by_path(self):
        playbook = factories.PlaybookFactory(path="/root/playbook.yml")
        factories.PlaybookFactory(path="/home/playbook.yml")

        # Test exact match
        request = self.client.get("/api/v1/playbooks?path=/root/playbook.yml")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(playbook.path, request.data["results"][0]["path"])

        # Test partial match
        request = self.client.get("/api/v1/playbooks?path=playbook.yml")
        self.assertEqual(len(request.data["results"]), 2)

    def test_patch_playbook_name(self):
        playbook = factories.PlaybookFactory()
        new_name = "foo"
        self.assertNotEqual(playbook.name, new_name)
        request = self.client.patch("/api/v1/playbooks/%s" % playbook.id, {"name": new_name})
        self.assertEqual(200, request.status_code)
        playbook_updated = models.Playbook.objects.get(id=playbook.id)
        self.assertEqual(playbook_updated.name, new_name)

    def test_get_playbook_by_status(self):
        playbook = factories.PlaybookFactory(status="failed")
        factories.PlaybookFactory(status="completed")
        factories.PlaybookFactory(status="running")

        # Confirm we have three objects
        request = self.client.get("/api/v1/playbooks")
        self.assertEqual(3, len(request.data["results"]))

        # Test single status
        request = self.client.get("/api/v1/playbooks?status=failed")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(playbook.status, request.data["results"][0]["status"])

        # Test multiple status
        request = self.client.get("/api/v1/playbooks?status=failed&status=completed")
        self.assertEqual(2, len(request.data["results"]))

    def test_get_playbook_duration(self):
        started = timezone.now()
        ended = started + datetime.timedelta(hours=1)
        playbook = factories.PlaybookFactory(started=started, ended=ended)
        request = self.client.get("/api/v1/playbooks/%s" % playbook.id)
        self.assertEqual(parse_duration(request.data["duration"]), ended - started)

    def test_get_playbook_by_date(self):
        playbook = factories.PlaybookFactory()

        past = datetime.datetime.now() - datetime.timedelta(hours=12)
        negative_date_fields = ["created_before", "started_before", "updated_before"]
        positive_date_fields = ["created_after", "started_after", "updated_after"]

        # Expect no playbook when searching before it was created
        for field in negative_date_fields:
            request = self.client.get("/api/v1/playbooks?%s=%s" % (field, past.isoformat()))
            self.assertEqual(request.data["count"], 0)

        # Expect a playbook when searching after it was created
        for field in positive_date_fields:
            request = self.client.get("/api/v1/playbooks?%s=%s" % (field, past.isoformat()))
            self.assertEqual(request.data["count"], 1)
            self.assertEqual(request.data["results"][0]["id"], playbook.id)

    def test_get_playbook_order(self):
        old_started = timezone.now() - datetime.timedelta(hours=12)
        old_ended = old_started + datetime.timedelta(minutes=30)
        old_playbook = factories.PlaybookFactory(started=old_started, ended=old_ended)
        new_started = timezone.now() - datetime.timedelta(hours=6)
        new_ended = new_started + datetime.timedelta(hours=1)
        new_playbook = factories.PlaybookFactory(started=new_started, ended=new_ended)

        # Ensure we have two objects
        request = self.client.get("/api/v1/playbooks")
        self.assertEqual(2, len(request.data["results"]))

        order_fields = ["id", "created", "updated", "started", "ended", "duration"]
        # Ascending order
        for field in order_fields:
            request = self.client.get("/api/v1/playbooks?order=%s" % field)
            self.assertEqual(request.data["results"][0]["id"], old_playbook.id)

        # Descending order
        for field in order_fields:
            request = self.client.get("/api/v1/playbooks?order=-%s" % field)
            self.assertEqual(request.data["results"][0]["id"], new_playbook.id)

    def test_patch_playbook_labels(self):
        playbook = factories.PlaybookFactory()
        labels = ["test-label", "another-test-label"]
        self.assertNotEqual(playbook.labels, labels)
        request = self.client.patch("/api/v1/playbooks/%s" % playbook.id, {"labels": labels})
        self.assertEqual(200, request.status_code)
        playbook_updated = models.Playbook.objects.get(id=playbook.id)
        self.assertEqual([label.name for label in playbook_updated.labels.all()], labels)

    def test_get_playbook_by_label(self):
        # Create two playbooks, one with labels and one without
        playbook = factories.PlaybookFactory()
        self.client.patch("/api/v1/playbooks/%s" % playbook.id, {"labels": ["test-label"]})
        factories.PlaybookFactory()

        # Ensure we have two objects when searching without labels
        request = self.client.get("/api/v1/playbooks")
        self.assertEqual(2, len(request.data["results"]))

        # Search with label and ensure we have the right one
        request = self.client.get("/api/v1/playbooks?label=%s" % "test-label")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(request.data["results"][0]["labels"][0]["name"], "test-label")
