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
            }
        )
        serializer.is_valid()
        result = serializer.save()
        result.refresh_from_db()
        self.assertEqual(result.status, "skipped")
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
            },
        )
        self.assertEqual(201, request.status_code)
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
        self.assertEqual(result.status, request.data["results"][0]["status"])
        self.assertEqual("skipped", request.data["results"][1]["status"])

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
        self.assertEqual(failed_result.status, results[0]["status"])
        self.assertEqual(skipped_result.status, results[1]["status"])
