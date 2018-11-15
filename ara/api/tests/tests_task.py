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


class TaskTestCase(APITestCase):
    def test_task_factory(self):
        task = factories.TaskFactory(name="factory")
        self.assertEqual(task.name, "factory")

    def test_task_serializer(self):
        play = factories.PlayFactory()
        file = factories.FileFactory()
        serializer = serializers.TaskSerializer(
            data={
                "name": "serializer",
                "action": "test",
                "lineno": 2,
                "status": "completed",
                "handler": False,
                "play": play.id,
                "file": file.id,
                "playbook": play.playbook.id,
            }
        )
        serializer.is_valid()
        task = serializer.save()
        task.refresh_from_db()
        self.assertEqual(task.name, "serializer")
        self.assertEqual(task.status, "completed")

    def test_task_serializer_compress_tags(self):
        play = factories.PlayFactory()
        file = factories.FileFactory()
        serializer = serializers.TaskSerializer(
            data={
                "name": "compress",
                "action": "test",
                "lineno": 2,
                "status": "running",
                "handler": False,
                "play": play.id,
                "file": file.id,
                "tags": factories.TASK_TAGS,
                "playbook": play.playbook.id,
            }
        )
        serializer.is_valid()
        task = serializer.save()
        task.refresh_from_db()
        self.assertEqual(task.tags, utils.compressed_obj(factories.TASK_TAGS))

    def test_task_serializer_decompress_tags(self):
        task = factories.TaskFactory(tags=utils.compressed_obj(factories.TASK_TAGS))
        serializer = serializers.TaskSerializer(instance=task)
        self.assertEqual(serializer.data["tags"], factories.TASK_TAGS)

    def test_get_no_tasks(self):
        request = self.client.get("/api/v1/tasks")
        self.assertEqual(0, len(request.data["results"]))

    def test_get_tasks(self):
        task = factories.TaskFactory()
        request = self.client.get("/api/v1/tasks")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(task.name, request.data["results"][0]["name"])

    def test_delete_task(self):
        task = factories.TaskFactory()
        self.assertEqual(1, models.Task.objects.all().count())
        request = self.client.delete("/api/v1/tasks/%s" % task.id)
        self.assertEqual(204, request.status_code)
        self.assertEqual(0, models.Task.objects.all().count())

    def test_create_task(self):
        play = factories.PlayFactory()
        file = factories.FileFactory()
        self.assertEqual(0, models.Task.objects.count())
        request = self.client.post(
            "/api/v1/tasks",
            {
                "name": "create",
                "action": "test",
                "lineno": 2,
                "handler": False,
                "status": "running",
                "play": play.id,
                "file": file.id,
                "playbook": play.playbook.id,
            },
        )
        self.assertEqual(201, request.status_code)
        self.assertEqual(1, models.Task.objects.count())

    def test_partial_update_task(self):
        task = factories.TaskFactory()
        self.assertNotEqual("update", task.name)
        request = self.client.patch("/api/v1/tasks/%s" % task.id, {"name": "update"})
        self.assertEqual(200, request.status_code)
        task_updated = models.Task.objects.get(id=task.id)
        self.assertEqual("update", task_updated.name)

    def test_get_task(self):
        task = factories.TaskFactory()
        request = self.client.get("/api/v1/tasks/%s" % task.id)
        self.assertEqual(task.name, request.data["name"])

    def test_get_tasks_by_playbook(self):
        playbook = factories.PlaybookFactory()
        task = factories.TaskFactory(name="task1", playbook=playbook)
        factories.TaskFactory(name="task2", playbook=playbook)
        request = self.client.get("/api/v1/tasks?playbook=%s" % playbook.id)
        self.assertEqual(2, len(request.data["results"]))
        self.assertEqual(task.name, request.data["results"][0]["name"])
        self.assertEqual("task2", request.data["results"][1]["name"])

    def test_get_task_duration(self):
        started = timezone.now()
        ended = started + datetime.timedelta(hours=1)
        task = factories.TaskFactory(started=started, ended=ended)
        request = self.client.get("/api/v1/tasks/%s" % task.id)
        self.assertEqual(request.data["duration"], datetime.timedelta(0, 3600))

    def test_update_wrong_task_status(self):
        task = factories.TaskFactory()
        self.assertNotEqual("wrong", task.status)
        request = self.client.patch("/api/v1/tasks/%s" % task.id, {"status": "wrong"})
        self.assertEqual(400, request.status_code)
        task_updated = models.Task.objects.get(id=task.id)
        self.assertNotEqual("wrong", task_updated.status)
