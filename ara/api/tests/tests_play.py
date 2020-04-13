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
from django.utils.dateparse import parse_duration
from rest_framework.test import APITestCase

from ara.api import models, serializers
from ara.api.tests import factories


class PlayTestCase(APITestCase):
    def test_play_factory(self):
        play = factories.PlayFactory(name="play factory")
        self.assertEqual(play.name, "play factory")

    def test_play_serializer(self):
        playbook = factories.PlaybookFactory()
        serializer = serializers.PlaySerializer(
            data={
                "name": "serializer",
                "status": "completed",
                "uuid": "5c5f67b9-e63c-6297-80da-000000000005",
                "playbook": playbook.id,
            }
        )
        serializer.is_valid()
        play = serializer.save()
        play.refresh_from_db()
        self.assertEqual(play.name, "serializer")
        self.assertEqual(play.status, "completed")

    def test_get_no_plays(self):
        request = self.client.get("/api/v1/plays")
        self.assertEqual(0, len(request.data["results"]))

    def test_get_plays(self):
        play = factories.PlayFactory()
        request = self.client.get("/api/v1/plays")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(play.name, request.data["results"][0]["name"])

    def test_delete_play(self):
        play = factories.PlayFactory()
        self.assertEqual(1, models.Play.objects.all().count())
        request = self.client.delete("/api/v1/plays/%s" % play.id)
        self.assertEqual(204, request.status_code)
        self.assertEqual(0, models.Play.objects.all().count())

    def test_create_play(self):
        playbook = factories.PlaybookFactory()
        self.assertEqual(0, models.Play.objects.count())
        request = self.client.post(
            "/api/v1/plays",
            {
                "name": "create",
                "status": "running",
                "uuid": "5c5f67b9-e63c-6297-80da-000000000005",
                "playbook": playbook.id,
            },
        )
        self.assertEqual(201, request.status_code)
        self.assertEqual(1, models.Play.objects.count())

    def test_partial_update_play(self):
        play = factories.PlayFactory()
        self.assertNotEqual("update", play.name)
        request = self.client.patch("/api/v1/plays/%s" % play.id, {"name": "update"})
        self.assertEqual(200, request.status_code)
        play_updated = models.Play.objects.get(id=play.id)
        self.assertEqual("update", play_updated.name)

    def test_get_play(self):
        play = factories.PlayFactory()
        request = self.client.get("/api/v1/plays/%s" % play.id)
        self.assertEqual(play.name, request.data["name"])

    def test_get_play_by_playbook(self):
        play = factories.PlayFactory(name="play1")
        factories.PlayFactory(name="play2")
        request = self.client.get("/api/v1/plays?playbook=1")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(play.name, request.data["results"][0]["name"])

    def test_get_plays_by_name(self):
        # Create a playbook and two plays
        playbook = factories.PlaybookFactory()
        play = factories.PlayFactory(name="first_play", playbook=playbook)
        factories.TaskFactory(name="second_play", playbook=playbook)

        # Query for the first play name and expect one result
        request = self.client.get("/api/v1/plays?name=%s" % play.name)
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(play.name, request.data["results"][0]["name"])

    def test_get_play_by_uuid(self):
        play = factories.PlayFactory(name="play1", uuid="6b838b6f-cfc7-4e11-a264-73df8683ee0e")
        factories.PlayFactory(name="play2")
        request = self.client.get("/api/v1/plays?uuid=6b838b6f-cfc7-4e11-a264-73df8683ee0e")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(play.name, request.data["results"][0]["name"])

    def test_get_play_duration(self):
        started = timezone.now()
        ended = started + datetime.timedelta(hours=1)
        play = factories.PlayFactory(started=started, ended=ended)
        request = self.client.get("/api/v1/plays/%s" % play.id)
        self.assertEqual(parse_duration(request.data["duration"]), ended - started)

    def test_get_play_by_date(self):
        play = factories.PlayFactory()

        past = datetime.datetime.now() - datetime.timedelta(hours=12)
        negative_date_fields = ["created_before", "started_before", "updated_before"]
        positive_date_fields = ["created_after", "started_after", "updated_after"]

        # Expect no play when searching before it was created
        for field in negative_date_fields:
            request = self.client.get("/api/v1/plays?%s=%s" % (field, past.isoformat()))
            self.assertEqual(request.data["count"], 0)

        # Expect a play when searching after it was created
        for field in positive_date_fields:
            request = self.client.get("/api/v1/plays?%s=%s" % (field, past.isoformat()))
            self.assertEqual(request.data["count"], 1)
            self.assertEqual(request.data["results"][0]["id"], play.id)

    def test_get_play_order(self):
        old_started = timezone.now() - datetime.timedelta(hours=12)
        old_ended = old_started + datetime.timedelta(minutes=30)
        old_play = factories.PlayFactory(started=old_started, ended=old_ended)
        new_started = timezone.now() - datetime.timedelta(hours=6)
        new_ended = new_started + datetime.timedelta(hours=1)
        new_play = factories.PlayFactory(started=new_started, ended=new_ended)

        # Ensure we have two objects
        request = self.client.get("/api/v1/plays")
        self.assertEqual(2, len(request.data["results"]))

        order_fields = ["id", "created", "updated", "started", "ended", "duration"]
        # Ascending order
        for field in order_fields:
            request = self.client.get("/api/v1/plays?order=%s" % field)
            self.assertEqual(request.data["results"][0]["id"], old_play.id)

        # Descending order
        for field in order_fields:
            request = self.client.get("/api/v1/plays?order=-%s" % field)
            self.assertEqual(request.data["results"][0]["id"], new_play.id)

    def test_update_wrong_play_status(self):
        play = factories.PlayFactory()
        self.assertNotEqual("wrong", play.status)
        request = self.client.patch("/api/v1/plays/%s" % play.id, {"status": "wrong"})
        self.assertEqual(400, request.status_code)
        play_updated = models.Play.objects.get(id=play.id)
        self.assertNotEqual("wrong", play_updated.status)

    def test_get_play_by_status(self):
        play = factories.PlayFactory(status="running")
        factories.PlayFactory(status="completed")
        factories.PlayFactory(status="unknown")

        # Confirm we have three objects
        request = self.client.get("/api/v1/plays")
        self.assertEqual(3, len(request.data["results"]))

        # Test single status
        request = self.client.get("/api/v1/plays?status=running")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(play.status, request.data["results"][0]["status"])

        # Test multiple status
        request = self.client.get("/api/v1/plays?status=running&status=completed")
        self.assertEqual(2, len(request.data["results"]))
