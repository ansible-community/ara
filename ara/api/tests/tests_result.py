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
from ara.api.tests import factories, utils


class ResultTestCase(APITestCase):
    def test_result_factory(self):
        result = factories.ResultFactory(status="failed")
        self.assertEqual(result.status, "failed")

    def test_result_serializer(self):
        host = factories.HostFactory()
        task = factories.TaskFactory()
        serializer = serializers.ResultSerializer(
            data={
                "status": "skipped",
                "host": host.id,
                "task": task.id,
                "play": task.play.id,
                "playbook": task.playbook.id,
                "changed": False,
                "ignore_errors": False,
            }
        )
        serializer.is_valid()
        result = serializer.save()
        result.refresh_from_db()
        self.assertEqual(result.status, "skipped")
        self.assertEqual(result.changed, False)
        self.assertEqual(result.ignore_errors, False)
        self.assertEqual(result.host.id, host.id)
        self.assertEqual(result.task.id, task.id)

    def test_result_serializer_compress_content(self):
        host = factories.HostFactory()
        task = factories.TaskFactory()
        serializer = serializers.ResultSerializer(
            data={
                "content": factories.RESULT_CONTENTS,
                "status": "changed",
                "host": host.id,
                "task": task.id,
                "play": task.play.id,
                "playbook": task.playbook.id,
            }
        )
        serializer.is_valid()
        result = serializer.save()
        result.refresh_from_db()
        self.assertEqual(result.content, utils.compressed_obj(factories.RESULT_CONTENTS))

    def test_result_serializer_decompress_content(self):
        result = factories.ResultFactory(content=utils.compressed_obj(factories.RESULT_CONTENTS))
        serializer = serializers.ResultSerializer(instance=result)
        self.assertEqual(serializer.data["content"], factories.RESULT_CONTENTS)

    def test_get_no_results(self):
        request = self.client.get("/api/v1/results")
        self.assertEqual(0, len(request.data["results"]))

    def test_get_results(self):
        result = factories.ResultFactory()
        request = self.client.get("/api/v1/results")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(result.status, request.data["results"][0]["status"])

    def test_delete_result(self):
        result = factories.ResultFactory()
        self.assertEqual(1, models.Result.objects.all().count())
        request = self.client.delete("/api/v1/results/%s" % result.id)
        self.assertEqual(204, request.status_code)
        self.assertEqual(0, models.Result.objects.all().count())

    def test_create_result(self):
        host = factories.HostFactory()
        task = factories.TaskFactory()
        self.assertEqual(0, models.Result.objects.count())
        request = self.client.post(
            "/api/v1/results",
            {
                "content": factories.RESULT_CONTENTS,
                "status": "ok",
                "host": host.id,
                "task": task.id,
                "play": task.play.id,
                "playbook": task.playbook.id,
                "changed": True,
                "ignore_errors": False,
            },
        )
        self.assertEqual(201, request.status_code)
        self.assertEqual(request.data["changed"], True)
        self.assertEqual(request.data["ignore_errors"], False)
        self.assertEqual(1, models.Result.objects.count())

    def test_partial_update_result(self):
        result = factories.ResultFactory()
        self.assertNotEqual("unreachable", result.status)
        request = self.client.patch("/api/v1/results/%s" % result.id, {"status": "unreachable"})
        self.assertEqual(200, request.status_code)
        result_updated = models.Result.objects.get(id=result.id)
        self.assertEqual("unreachable", result_updated.status)

    def test_get_result(self):
        result = factories.ResultFactory()
        request = self.client.get("/api/v1/results/%s" % result.id)
        self.assertEqual(result.status, request.data["status"])

    def test_get_result_by_playbook(self):
        playbook = factories.PlaybookFactory()
        host_one = factories.HostFactory(name="one")
        host_two = factories.HostFactory(name="two")
        result = factories.ResultFactory(playbook=playbook, host=host_one, status="failed")
        factories.ResultFactory(playbook=playbook, host=host_two, status="skipped")
        request = self.client.get("/api/v1/results?playbook=%s" % playbook.id)
        self.assertEqual(2, len(request.data["results"]))
        self.assertEqual(result.status, request.data["results"][1]["status"])
        self.assertEqual("skipped", request.data["results"][0]["status"])

    def test_get_result_by_statuses(self):
        failed_result = factories.ResultFactory(status="failed")
        skipped_result = factories.ResultFactory(status="skipped")
        factories.ResultFactory(status="ok")
        results = self.client.get("/api/v1/results").data["results"]
        self.assertEqual(3, len(results))

        results = self.client.get("/api/v1/results?status=failed").data["results"]
        self.assertEqual(1, len(results))
        self.assertEqual(failed_result.status, results[0]["status"])

        results = self.client.get("/api/v1/results?status=skipped").data["results"]
        self.assertEqual(1, len(results))
        self.assertEqual(skipped_result.status, results[0]["status"])

        results = self.client.get("/api/v1/results?status=failed&status=skipped").data["results"]
        self.assertEqual(2, len(results))
        self.assertEqual(failed_result.status, results[1]["status"])
        self.assertEqual(skipped_result.status, results[0]["status"])

    def test_result_status_serializer(self):
        ok = factories.ResultFactory(status="ok")
        result = self.client.get("/api/v1/results/%s" % ok.id)
        self.assertEqual(result.data["status"], "ok")

        changed = factories.ResultFactory(status="ok", changed=True)
        result = self.client.get("/api/v1/results/%s" % changed.id)
        self.assertEqual(result.data["status"], "changed")

        failed = factories.ResultFactory(status="failed")
        result = self.client.get("/api/v1/results/%s" % failed.id)
        self.assertEqual(result.data["status"], "failed")

        ignored = factories.ResultFactory(status="failed", ignore_errors=True)
        result = self.client.get("/api/v1/results/%s" % ignored.id)
        self.assertEqual(result.data["status"], "ignored")

        skipped = factories.ResultFactory(status="skipped")
        result = self.client.get("/api/v1/results/%s" % skipped.id)
        self.assertEqual(result.data["status"], "skipped")

        unreachable = factories.ResultFactory(status="unreachable")
        result = self.client.get("/api/v1/results/%s" % unreachable.id)
        self.assertEqual(result.data["status"], "unreachable")

    def test_get_result_with_ignore_errors(self):
        failed = factories.ResultFactory(status="failed", ignore_errors=False)
        ignored = factories.ResultFactory(status="failed", ignore_errors=True)

        # Searching for failed should return both
        results = self.client.get("/api/v1/results?status=failed").data["results"]
        self.assertEqual(2, len(results))

        # Searching for failed with ignore_errors=True should only return the ignored result
        results = self.client.get("/api/v1/results?status=failed&ignore_errors=true").data["results"]
        self.assertEqual(1, len(results))
        self.assertEqual(ignored.id, results[0]["id"])

        # Searching for failed with ignore_errors=False should only return the failed result
        results = self.client.get("/api/v1/results?status=failed&ignore_errors=false").data["results"]
        self.assertEqual(1, len(results))
        self.assertEqual(failed.id, results[0]["id"])

    def test_get_result_duration(self):
        started = timezone.now()
        ended = started + datetime.timedelta(hours=1)
        result = factories.ResultFactory(started=started, ended=ended)
        request = self.client.get("/api/v1/results/%s" % result.id)
        self.assertEqual(parse_duration(request.data["duration"]), ended - started)

    def test_get_result_by_date(self):
        result = factories.ResultFactory()

        past = datetime.datetime.now() - datetime.timedelta(hours=12)
        negative_date_fields = ["created_before", "started_before", "updated_before"]
        positive_date_fields = ["created_after", "started_after", "updated_after"]

        # Expect no result when searching before it was created
        for field in negative_date_fields:
            request = self.client.get("/api/v1/results?%s=%s" % (field, past.isoformat()))
            self.assertEqual(request.data["count"], 0)

        # Expect a result when searching after it was created
        for field in positive_date_fields:
            request = self.client.get("/api/v1/results?%s=%s" % (field, past.isoformat()))
            self.assertEqual(request.data["count"], 1)
            self.assertEqual(request.data["results"][0]["id"], result.id)

    def test_get_result_order(self):
        old_started = timezone.now() - datetime.timedelta(hours=12)
        old_ended = old_started + datetime.timedelta(minutes=30)
        old_result = factories.ResultFactory(started=old_started, ended=old_ended)
        new_started = timezone.now() - datetime.timedelta(hours=6)
        new_ended = new_started + datetime.timedelta(hours=1)
        new_result = factories.ResultFactory(started=new_started, ended=new_ended)

        # Ensure we have two objects
        request = self.client.get("/api/v1/results")
        self.assertEqual(2, len(request.data["results"]))

        order_fields = ["id", "created", "updated", "started", "ended", "duration"]
        # Ascending order
        for field in order_fields:
            request = self.client.get("/api/v1/results?order=%s" % field)
            self.assertEqual(request.data["results"][0]["id"], old_result.id)

        # Descending order
        for field in order_fields:
            request = self.client.get("/api/v1/results?order=-%s" % field)
            self.assertEqual(request.data["results"][0]["id"], new_result.id)
