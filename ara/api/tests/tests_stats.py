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

from ara.api import models, serializers
from ara.api.tests import factories


class StatsTestCase(APITestCase):
    def test_stats_factory(self):
        stats = factories.StatsFactory(changed=2, failed=1, ok=3, skipped=2, unreachable=1)
        self.assertEqual(stats.changed, 2)
        self.assertEqual(stats.failed, 1)
        self.assertEqual(stats.ok, 3)
        self.assertEqual(stats.skipped, 2)
        self.assertEqual(stats.unreachable, 1)

    def test_stats_serializer(self):
        playbook = factories.PlaybookFactory()
        host = factories.HostFactory()
        serializer = serializers.StatsSerializer(data=dict(playbook=playbook.id, host=host.id, ok=9001))
        serializer.is_valid()
        stats = serializer.save()
        stats.refresh_from_db()
        self.assertEqual(stats.playbook.id, playbook.id)
        self.assertEqual(stats.host.id, host.id)
        self.assertEqual(stats.ok, 9001)

    def test_create_stats(self):
        playbook = factories.PlaybookFactory()
        host = factories.HostFactory()
        self.assertEqual(0, models.Stats.objects.count())
        request = self.client.post("/api/v1/stats", dict(playbook=playbook.id, host=host.id, ok=9001))
        self.assertEqual(201, request.status_code)
        self.assertEqual(1, models.Stats.objects.count())

    def test_get_no_stats(self):
        request = self.client.get("/api/v1/stats")
        self.assertEqual(0, len(request.data["results"]))

    def test_get_stats(self):
        stats = factories.StatsFactory()
        request = self.client.get("/api/v1/stats")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(stats.ok, request.data["results"][0]["ok"])

    def test_get_stats_by_playbook(self):
        playbook = factories.PlaybookFactory()
        host_one = factories.HostFactory(name="one")
        host_two = factories.HostFactory(name="two")
        stats = factories.StatsFactory(host=host_one, playbook=playbook, ok=9001)
        factories.StatsFactory(host=host_two, playbook=playbook)
        request = self.client.get("/api/v1/stats?playbook=%s" % playbook.id)
        self.assertEqual(2, len(request.data["results"]))
        self.assertEqual(host_one.id, request.data["results"][0]["id"])
        self.assertEqual(stats.ok, request.data["results"][0]["ok"])
        self.assertEqual(host_two.id, request.data["results"][1]["id"])

    def test_get_stats_by_host(self):
        playbook = factories.PlaybookFactory()
        host_one = factories.HostFactory(name="one")
        host_two = factories.HostFactory(name="two")
        stats = factories.StatsFactory(host=host_one, playbook=playbook, ok=9001)
        factories.StatsFactory(host=host_two, playbook=playbook)
        request = self.client.get("/api/v1/stats?host=%s" % host_one.id)
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(stats.ok, request.data["results"][0]["ok"])
        self.assertEqual(host_one.id, request.data["results"][0]["id"])

    def test_get_stats_id(self):
        stats = factories.StatsFactory()
        request = self.client.get("/api/v1/stats/%s" % stats.id)
        self.assertEqual(stats.ok, request.data["ok"])

    def test_partial_update_stats(self):
        stats = factories.StatsFactory()
        self.assertNotEqual(9001, stats.ok)
        request = self.client.patch("/api/v1/stats/%s" % stats.id, dict(ok=9001))
        self.assertEqual(200, request.status_code)
        stats_updated = models.Stats.objects.get(id=stats.id)
        self.assertEqual(9001, stats_updated.ok)

    def test_delete_stats(self):
        stats = factories.StatsFactory()
        self.assertEqual(1, models.Stats.objects.all().count())
        request = self.client.delete("/api/v1/stats/%s" % stats.id)
        self.assertEqual(204, request.status_code)
        self.assertEqual(0, models.Stats.objects.all().count())
