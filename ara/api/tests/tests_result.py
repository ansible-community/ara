# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

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

    def test_result_serializer_without_delegation(self):
        host = factories.HostFactory(name="first")
        task = factories.TaskFactory()
        serializer = serializers.ResultSerializer(
            data={
                "status": "skipped",
                "host": host.id,
                "delegated_to": [],
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
        # FIXME: Why does the serializer return a ManyRelatedManager queryset for delegated_to ?
        from_queryset = list(result.delegated_to.values())
        self.assertEqual(from_queryset, [])
        self.assertEqual(result.task.id, task.id)

    def test_result_serializer_with_delegation(self):
        host = factories.HostFactory(name="first")
        anotherhost = factories.HostFactory(name="second")
        task = factories.TaskFactory()
        serializer = serializers.ResultSerializer(
            data={
                "status": "skipped",
                "host": host.id,
                "delegated_to": [anotherhost.id],
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
        # FIXME: Why does the serializer return a ManyRelatedManager queryset for delegated_to ?
        self.assertEqual(result.delegated_to.values()[0]["id"], anotherhost.id)
        self.assertEqual(result.delegated_to.values()[0]["name"], anotherhost.name)
        self.assertEqual(result.task.id, task.id)

    def test_result_serializer_compress_content(self):
        host = factories.HostFactory()
        task = factories.TaskFactory()
        serializer = serializers.ResultSerializer(
            data={
                "content": factories.RESULT_CONTENTS,
                "status": "ok",
                "host": host.id,
                "delegated_to": [],
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
                "delegated_to": [],
                "task": task.id,
                "play": task.play.id,
                "playbook": task.playbook.id,
                "changed": True,
                "ignore_errors": False,
            },
        )
        self.assertEqual(201, request.status_code)
        self.assertEqual(1, models.Result.objects.count())
        self.assertEqual(request.data["changed"], True)
        self.assertEqual(request.data["ignore_errors"], False)
        self.assertEqual(request.data["status"], "ok")
        self.assertEqual(request.data["host"], host.id)
        self.assertEqual(request.data["delegated_to"], [])
        self.assertEqual(request.data["task"], task.id)
        self.assertEqual(request.data["play"], task.play.id)
        self.assertEqual(request.data["playbook"], task.playbook.id)

    def test_create_result_with_delegation(self):
        host = factories.HostFactory(name="original")
        delegated_host = factories.HostFactory(name="delegated")
        task = factories.TaskFactory()
        self.assertEqual(0, models.Result.objects.count())
        request = self.client.post(
            "/api/v1/results",
            {
                "content": factories.RESULT_CONTENTS,
                "status": "ok",
                "host": host.id,
                "delegated_to": [delegated_host.id],
                "task": task.id,
                "play": task.play.id,
                "playbook": task.playbook.id,
                "changed": True,
                "ignore_errors": False,
            },
        )
        self.assertEqual(201, request.status_code)
        self.assertEqual(1, models.Result.objects.count())
        self.assertEqual(request.data["changed"], True)
        self.assertEqual(request.data["ignore_errors"], False)
        self.assertEqual(request.data["status"], "ok")
        self.assertEqual(request.data["host"], host.id)
        self.assertEqual(request.data["delegated_to"], [delegated_host.id])
        self.assertEqual(request.data["task"], task.id)
        self.assertEqual(request.data["play"], task.play.id)
        self.assertEqual(request.data["playbook"], task.playbook.id)

    def test_create_result_with_two_delegations(self):
        host = factories.HostFactory(name="original")
        delegated_host = factories.HostFactory(name="delegated")
        another_host = factories.HostFactory(name="another")
        task = factories.TaskFactory()
        self.assertEqual(0, models.Result.objects.count())
        request = self.client.post(
            "/api/v1/results",
            {
                "content": factories.RESULT_CONTENTS,
                "status": "ok",
                "host": host.id,
                "delegated_to": [delegated_host.id, another_host.id],
                "task": task.id,
                "play": task.play.id,
                "playbook": task.playbook.id,
                "changed": True,
                "ignore_errors": False,
            },
        )
        self.assertEqual(201, request.status_code)
        self.assertEqual(1, models.Result.objects.count())
        self.assertEqual(request.data["changed"], True)
        self.assertEqual(request.data["ignore_errors"], False)
        self.assertEqual(request.data["status"], "ok")
        self.assertEqual(request.data["host"], host.id)
        self.assertEqual(request.data["delegated_to"], [delegated_host.id, another_host.id])
        self.assertEqual(request.data["task"], task.id)
        self.assertEqual(request.data["play"], task.play.id)
        self.assertEqual(request.data["playbook"], task.playbook.id)

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

    def test_get_result_by_association(self):
        # Create two results in necessarily two different playbooks with different children:
        # playbook -> play -> task -> result <- host
        first_result = factories.ResultFactory()
        second_result = factories.ResultFactory()

        # the fields with the association ids
        associations = ["playbook", "play", "task", "host"]

        # Validate that we somehow didn't wind up with the same association ids
        for association in associations:
            first = getattr(first_result, association)
            second = getattr(second_result, association)
            self.assertNotEqual(first.id, second.id)

        # In other words, there must be two distinct results
        request = self.client.get("/api/v1/results")
        self.assertEqual(2, request.data["count"])
        self.assertEqual(2, len(request.data["results"]))

        # Searching for the first_result associations should only yield one result
        for association in associations:
            assoc_id = getattr(first_result, association).id
            results = self.client.get("/api/v1/results?%s=%s" % (association, assoc_id))
            self.assertEqual(1, results.data["count"])
            self.assertEqual(1, len(results.data["results"]))
            self.assertEqual(assoc_id, results.data["results"][0][association])

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

    def test_get_changed_results(self):
        changed_result = factories.ResultFactory(changed=True)
        unchanged_result = factories.ResultFactory(changed=False)

        # Assert two results
        results = self.client.get("/api/v1/results").data["results"]
        self.assertEqual(2, len(results))

        # Assert one changed
        results = self.client.get("/api/v1/results?changed=true").data["results"]
        self.assertEqual(1, len(results))
        self.assertEqual(results[0]["id"], changed_result.id)

        # Assert one unchanged
        results = self.client.get("/api/v1/results?changed=false").data["results"]
        self.assertEqual(1, len(results))
        self.assertEqual(results[0]["id"], unchanged_result.id)

    def test_get_playbook_arguments(self):
        result = factories.ResultFactory()
        request = self.client.get("/api/v1/results/%s" % result.id)
        self.assertIn("inventory", request.data["playbook"]["arguments"])
