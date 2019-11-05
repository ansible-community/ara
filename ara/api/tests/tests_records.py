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


class RecordTestCase(APITestCase):
    def test_record_factory(self):
        record = factories.RecordFactory(key="test")
        self.assertEqual(record.key, "test")

    def test_record_serializer(self):
        playbook = factories.PlaybookFactory()
        serializer = serializers.RecordSerializer(
            data={"key": "test", "value": factories.RECORD_LIST, "type": "list", "playbook": playbook.id}
        )
        serializer.is_valid()
        record = serializer.save()
        record.refresh_from_db()
        self.assertEqual(record.key, "test")
        self.assertEqual(record.value, utils.compressed_obj(factories.RECORD_LIST))
        self.assertEqual(record.type, "list")

    def test_get_no_records(self):
        request = self.client.get("/api/v1/records")
        self.assertEqual(0, len(request.data["results"]))

    def test_get_record(self):
        record = factories.RecordFactory()
        request = self.client.get("/api/v1/records")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(record.key, request.data["results"][0]["key"])

    def test_delete_record(self):
        record = factories.RecordFactory()
        self.assertEqual(1, models.Record.objects.all().count())
        request = self.client.delete("/api/v1/records/%s" % record.id)
        self.assertEqual(204, request.status_code)
        self.assertEqual(0, models.Record.objects.all().count())

    def test_create_text_record(self):
        playbook = factories.PlaybookFactory()
        self.assertEqual(0, models.Record.objects.count())
        request = self.client.post(
            "/api/v1/records", {"key": "test", "value": "value", "type": "text", "playbook": playbook.id}
        )
        self.assertEqual(201, request.status_code)
        self.assertEqual(1, models.Record.objects.count())

    def test_create_list_record(self):
        playbook = factories.PlaybookFactory()
        self.assertEqual(0, models.Record.objects.count())
        test_list = factories.RECORD_LIST
        request = self.client.post(
            "/api/v1/records", {"key": "listrecord", "value": test_list, "type": "list", "playbook": playbook.id}
        )
        self.assertEqual(201, request.status_code)
        self.assertEqual(1, models.Record.objects.count())
        self.assertEqual(test_list, request.data["value"])

    def test_create_dict_record(self):
        playbook = factories.PlaybookFactory()
        self.assertEqual(0, models.Record.objects.count())
        test_dict = {"a": "dictionary"}
        request = self.client.post(
            "/api/v1/records", {"key": "dictrecord", "value": test_dict, "type": "dict", "playbook": playbook.id}
        )
        self.assertEqual(201, request.status_code)
        self.assertEqual(1, models.Record.objects.count())
        self.assertEqual(test_dict, request.data["value"])

    def test_create_json_record(self):
        playbook = factories.PlaybookFactory()
        self.assertEqual(0, models.Record.objects.count())
        test_json = '{"a": "dictionary"}'
        request = self.client.post(
            "/api/v1/records", {"key": "dictrecord", "value": test_json, "type": "json", "playbook": playbook.id}
        )
        self.assertEqual(201, request.status_code)
        self.assertEqual(1, models.Record.objects.count())
        self.assertEqual(test_json, request.data["value"])

    def test_create_url_record(self):
        playbook = factories.PlaybookFactory()
        self.assertEqual(0, models.Record.objects.count())
        test_url = "https://ara.recordsansible.org"
        request = self.client.post(
            "/api/v1/records", {"key": "dictrecord", "value": test_url, "type": "url", "playbook": playbook.id}
        )
        self.assertEqual(201, request.status_code)
        self.assertEqual(1, models.Record.objects.count())
        self.assertEqual(test_url, request.data["value"])

    def test_partial_update_record(self):
        record = factories.RecordFactory()
        self.assertNotEqual("update", record.key)
        request = self.client.patch("/api/v1/records/%s" % record.id, {"key": "update"})
        self.assertEqual(200, request.status_code)
        record_updated = models.Record.objects.get(id=record.id)
        self.assertEqual("update", record_updated.key)

    def test_get_records_by_playbook(self):
        playbook = factories.PlaybookFactory()
        record = factories.RecordFactory(playbook=playbook, key="by_playbook")
        factories.RecordFactory(key="another_record")
        request = self.client.get("/api/v1/records?playbook=%s" % playbook.id)
        self.assertEqual(2, models.Record.objects.all().count())
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(record.key, request.data["results"][0]["key"])
        self.assertEqual(record.playbook.id, request.data["results"][0]["playbook"])

    def test_get_records_by_key(self):
        playbook = factories.PlaybookFactory()
        record = factories.RecordFactory(playbook=playbook, key="by_key")
        factories.RecordFactory(key="another_record")
        request = self.client.get("/api/v1/records?key=%s" % record.key)
        self.assertEqual(2, models.Record.objects.all().count())
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(record.key, request.data["results"][0]["key"])
        self.assertEqual(record.playbook.id, request.data["results"][0]["playbook"])

    def test_get_records_by_playbook_and_key(self):
        playbook = factories.PlaybookFactory()
        record = factories.RecordFactory(playbook=playbook, key="by_playbook_and_key")
        factories.RecordFactory(playbook=playbook, key="another_record_in_playbook")
        factories.RecordFactory(key="another_record_in_another_playbook")
        request = self.client.get("/api/v1/records?playbook=%s&key=%s" % (playbook.id, record.key))
        self.assertEqual(3, models.Record.objects.all().count())
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(record.key, request.data["results"][0]["key"])
        self.assertEqual(record.playbook.id, request.data["results"][0]["playbook"])

    def test_get_record_by_date(self):
        record = factories.RecordFactory()

        past = datetime.datetime.now() - datetime.timedelta(hours=12)
        negative_date_fields = ["created_before", "updated_before"]
        positive_date_fields = ["created_after", "updated_after"]

        # Expect no record when searching before it was created
        for field in negative_date_fields:
            request = self.client.get("/api/v1/records?%s=%s" % (field, past.isoformat()))
            self.assertEqual(request.data["count"], 0)

        # Expect a record when searching after it was created
        for field in positive_date_fields:
            request = self.client.get("/api/v1/records?%s=%s" % (field, past.isoformat()))
            self.assertEqual(request.data["count"], 1)
            self.assertEqual(request.data["results"][0]["id"], record.id)

    def test_get_record_order(self):
        first_record = factories.RecordFactory(key="alpha")
        second_record = factories.RecordFactory(key="beta")

        # Ensure we have two objects
        request = self.client.get("/api/v1/records")
        self.assertEqual(2, len(request.data["results"]))

        order_fields = ["id", "created", "updated", "key"]
        # Ascending order
        for field in order_fields:
            request = self.client.get("/api/v1/records?order=%s" % field)
            self.assertEqual(request.data["results"][0]["id"], first_record.id)

        # Descending order
        for field in order_fields:
            request = self.client.get("/api/v1/records?order=-%s" % field)
            self.assertEqual(request.data["results"][0]["id"], second_record.id)
