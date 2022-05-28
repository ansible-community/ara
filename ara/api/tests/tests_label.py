# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import datetime

from django.db.utils import IntegrityError
from rest_framework.test import APITestCase

from ara.api import models, serializers
from ara.api.tests import factories


class LabelTestCase(APITestCase):
    def test_label_factory(self):
        label = factories.LabelFactory(name="factory")
        self.assertEqual(label.name, "factory")

    def test_label_serializer(self):
        serializer = serializers.LabelSerializer(data={"name": "serializer"})
        serializer.is_valid()
        label = serializer.save()
        label.refresh_from_db()
        self.assertEqual(label.name, "serializer")

    def test_create_label(self):
        self.assertEqual(0, models.Label.objects.count())
        request = self.client.post("/api/v1/labels", {"name": "compress"})
        self.assertEqual(201, request.status_code)
        self.assertEqual(1, models.Label.objects.count())

    def test_get_no_labels(self):
        request = self.client.get("/api/v1/labels")
        self.assertEqual(0, len(request.data["results"]))

    def test_get_labels(self):
        label = factories.LabelFactory()
        request = self.client.get("/api/v1/labels")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(label.name, request.data["results"][0]["name"])

    def test_get_label(self):
        label = factories.LabelFactory()
        request = self.client.get("/api/v1/labels/%s" % label.id)
        self.assertEqual(label.name, request.data["name"])

    def test_partial_update_label(self):
        label = factories.LabelFactory()
        self.assertNotEqual("updated", label.name)
        request = self.client.patch("/api/v1/labels/%s" % label.id, {"name": "updated"})
        self.assertEqual(200, request.status_code)
        label_updated = models.Label.objects.get(id=label.id)
        self.assertEqual("updated", label_updated.name)

    def test_delete_label(self):
        label = factories.LabelFactory()
        self.assertEqual(1, models.Label.objects.all().count())
        request = self.client.delete("/api/v1/labels/%s" % label.id)
        self.assertEqual(204, request.status_code)
        self.assertEqual(0, models.Label.objects.all().count())

    def test_get_label_by_date(self):
        label = factories.LabelFactory()

        past = datetime.datetime.now() - datetime.timedelta(hours=12)
        negative_date_fields = ["created_before", "updated_before"]
        positive_date_fields = ["created_after", "updated_after"]

        # Expect no label when searching before it was created
        for field in negative_date_fields:
            request = self.client.get("/api/v1/labels?%s=%s" % (field, past.isoformat()))
            self.assertEqual(request.data["count"], 0)

        # Expect a label when searching after it was created
        for field in positive_date_fields:
            request = self.client.get("/api/v1/labels?%s=%s" % (field, past.isoformat()))
            self.assertEqual(request.data["count"], 1)
            self.assertEqual(request.data["results"][0]["id"], label.id)

    def test_get_label_order(self):
        first_label = factories.LabelFactory(name="first")
        second_label = factories.LabelFactory(name="second")

        # Ensure we have two objects
        request = self.client.get("/api/v1/labels")
        self.assertEqual(2, len(request.data["results"]))

        order_fields = ["id", "created", "updated"]
        # Ascending order
        for field in order_fields:
            request = self.client.get("/api/v1/labels?order=%s" % field)
            self.assertEqual(request.data["results"][0]["name"], first_label.name)

        # Descending order
        for field in order_fields:
            request = self.client.get("/api/v1/labels?order=-%s" % field)
            self.assertEqual(request.data["results"][0]["name"], second_label.name)

    def test_unique_label_names(self):
        # Create a first label
        factories.LabelFactory(name="label")
        with self.assertRaises(IntegrityError):
            # Creating a second label with the same name should yield an exception
            factories.LabelFactory(name="label")
