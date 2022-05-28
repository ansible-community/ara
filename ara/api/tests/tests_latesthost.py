# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import time

from rest_framework.test import APITestCase

from ara.api import models, serializers
from ara.api.tests import factories


class LatestHostTestCase(APITestCase):
    def test_latesthost_factory(self):
        # TODO: Why doesn't the name propagate to "latest" in factories.LatestHostFactory(name="testhost") ?
        host = factories.HostFactory(name="testhost")
        latest_host = factories.LatestHostFactory(name="testhost", host=host)
        self.assertEqual(host.name, "testhost")
        self.assertEqual(latest_host.host.name, "testhost")

    def test_latesthost_serializer(self):
        playbook = factories.PlaybookFactory()
        serializer = serializers.HostSerializer(data={"name": "serializer", "playbook": playbook.id})
        serializer.is_valid()
        host = serializer.save()
        host.refresh_from_db()

        self.assertEqual(host.name, "serializer")
        self.assertEqual(host.playbook.id, playbook.id)

        request = self.client.get("/api/v1/latesthosts")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(request.data["results"][0]["name"], "serializer")

    def test_get_no_latesthosts(self):
        request = self.client.get("/api/v1/latesthosts")
        self.assertEqual(0, len(request.data["results"]))

    def test_get_latesthosts(self):
        # TODO: Why doesn't the name propagate to "latest" in factories.LatestHostFactory(name="testhost") ?
        host = factories.HostFactory(name="gethosts")
        latest_host = factories.LatestHostFactory(name="gethosts", host=host)
        request = self.client.get("/api/v1/latesthosts")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(latest_host.name, request.data["results"][0]["name"])
        self.assertEqual(latest_host.name, request.data["results"][0]["host"]["name"])

    def test_create_latesthost(self):
        playbook = factories.PlaybookFactory()
        self.assertEqual(0, models.Host.objects.count())
        self.assertEqual(0, models.LatestHost.objects.count())

        request = self.client.post("/api/v1/hosts", {"name": "create", "playbook": playbook.id})
        self.assertEqual(201, request.status_code)
        self.assertEqual("create", request.data["name"])
        self.assertEqual(1, models.Host.objects.count())
        self.assertEqual(1, models.LatestHost.objects.count())

        request = self.client.get("/api/v1/latesthosts")
        self.assertEqual("create", request.data["results"][0]["name"])
        self.assertEqual("create", request.data["results"][0]["host"]["name"])

    def test_delete_latesthost(self):
        playbook = factories.PlaybookFactory()
        self.assertEqual(0, models.Host.objects.count())
        self.assertEqual(0, models.LatestHost.objects.count())

        request = self.client.post("/api/v1/hosts", {"name": "create", "playbook": playbook.id})
        self.assertEqual(201, request.status_code)
        self.assertEqual("create", request.data["name"])
        self.assertEqual(1, models.Host.objects.count())
        self.assertEqual(1, models.LatestHost.objects.count())

        delete = self.client.delete("/api/v1/hosts/%s" % request.data["id"])
        self.assertEqual(204, delete.status_code)
        self.assertEqual(0, models.Host.objects.count())
        self.assertEqual(0, models.LatestHost.objects.count())

    def test_delete_and_update_latesthost(self):
        # Create two playbooks and two hosts
        first_playbook = factories.PlaybookFactory()
        second_playbook = factories.PlaybookFactory()

        first_host = self.client.post("/api/v1/hosts", {"name": "localhost", "playbook": first_playbook.id})
        # Slow this down a bit so we have a second host that is more noticeably "latest"
        time.sleep(0.2)
        second_host = self.client.post("/api/v1/hosts", {"name": "localhost", "playbook": second_playbook.id})

        self.assertEqual(2, models.Host.objects.count())
        self.assertEqual(1, models.LatestHost.objects.count())
        self.assertEqual(second_host.data["id"], models.LatestHost.objects.first().host.id)

        # Deleting the second host should update the latesthost to point to the first host
        delete = self.client.delete("/api/v1/hosts/%s" % second_host.data["id"])
        self.assertEqual(204, delete.status_code)
        self.assertEqual(1, models.Host.objects.count())
        self.assertEqual(first_host.data["id"], models.LatestHost.objects.first().host.id)

    def test_delete_without_update_latesthost(self):
        # Create two playbooks and two hosts
        first_playbook = factories.PlaybookFactory()
        second_playbook = factories.PlaybookFactory()

        first_host = self.client.post("/api/v1/hosts", {"name": "localhost", "playbook": first_playbook.id})
        # Slow this down a bit so we have a second host that is more noticeably "latest"
        time.sleep(0.2)
        second_host = self.client.post("/api/v1/hosts", {"name": "localhost", "playbook": second_playbook.id})

        self.assertEqual(2, models.Host.objects.count())
        self.assertEqual(1, models.LatestHost.objects.count())
        self.assertEqual(second_host.data["id"], models.LatestHost.objects.first().host.id)

        # Deleting the first host shouldn't result in an update to the latesthost table
        delete = self.client.delete("/api/v1/hosts/%s" % first_host.data["id"])
        self.assertEqual(204, delete.status_code)
        self.assertEqual(1, models.Host.objects.count())
        self.assertEqual(second_host.data["id"], models.LatestHost.objects.first().host.id)

    def test_delete_and_update_latesthost_via_playbook(self):
        # Create two playbooks and two hosts
        first_playbook = factories.PlaybookFactory()
        second_playbook = factories.PlaybookFactory()

        first_host = self.client.post("/api/v1/hosts", {"name": "localhost", "playbook": first_playbook.id})
        # Slow this down a bit so we have a second host that is more noticeably "latest"
        time.sleep(0.2)
        second_host = self.client.post("/api/v1/hosts", {"name": "localhost", "playbook": second_playbook.id})

        self.assertEqual(2, models.Host.objects.count())
        self.assertEqual(1, models.LatestHost.objects.count())
        self.assertEqual(second_host.data["id"], models.LatestHost.objects.first().host.id)

        # Deleting the second playbook should update the latesthost to point to the first host
        delete = self.client.delete("/api/v1/playbooks/%s" % second_playbook.id)
        self.assertEqual(204, delete.status_code)
        self.assertEqual(1, models.Host.objects.count())
        self.assertEqual(first_host.data["id"], models.LatestHost.objects.first().host.id)
