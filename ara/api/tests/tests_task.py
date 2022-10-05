# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import datetime

from django.utils import timezone
from django.utils.dateparse import parse_duration
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
                "uuid": "5c5f67b9-e63c-6297-80da-000000000009",
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
        self.assertEqual(str(task.uuid), "5c5f67b9-e63c-6297-80da-000000000009")
        self.assertEqual(task.status, "completed")

    def test_task_serializer_compress_tags(self):
        play = factories.PlayFactory()
        file = factories.FileFactory()
        serializer = serializers.TaskSerializer(
            data={
                "name": "compress",
                "uuid": "5c5f67b9-e63c-6297-80da-000000000009",
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
                "uuid": "5c5f67b9-e63c-6297-80da-000000000009",
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

    def test_expired_task(self):
        task = factories.TaskFactory(status="running")
        self.assertEqual("running", task.status)

        request = self.client.patch("/api/v1/tasks/%s" % task.id, {"status": "expired"})
        self.assertEqual(200, request.status_code)
        task_updated = models.Task.objects.get(id=task.id)
        self.assertEqual("expired", task_updated.status)

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
        self.assertEqual(task.name, request.data["results"][1]["name"])
        self.assertEqual("task2", request.data["results"][0]["name"])

    def test_get_tasks_by_play(self):
        playbook = factories.PlaybookFactory()
        # Create two plays
        play = factories.PlayFactory(name="first_play", playbook=playbook)
        second_play = factories.PlayFactory(name="second_play", playbook=playbook)
        request = self.client.get("/api/v1/plays")
        self.assertEqual(2, len(request.data["results"]))

        # Add tasks for the first play and validate
        task = factories.TaskFactory(name="inside_first", play=play)
        factories.TaskFactory(name="inside_second", play=play)

        request = self.client.get("/api/v1/tasks?play=%s" % play.id)
        self.assertEqual(2, len(request.data["results"]))
        self.assertEqual(task.name, request.data["results"][1]["name"])
        self.assertEqual("inside_second", request.data["results"][0]["name"])

        request = self.client.get("/api/v1/tasks?play=%s" % second_play.id)
        self.assertEqual(0, len(request.data["results"]))

    def test_get_tasks_by_name(self):
        # Create a playbook and two tasks
        playbook = factories.PlaybookFactory()
        task = factories.TaskFactory(name="task1", playbook=playbook)
        factories.TaskFactory(name="task2", playbook=playbook)

        # Query for the first task name and expect one result
        request = self.client.get("/api/v1/tasks?name=%s" % task.name)
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(task.name, request.data["results"][0]["name"])

    def test_get_tasks_by_uuid(self):
        # Create a playbook and two tasks
        playbook = factories.PlaybookFactory()
        task = factories.TaskFactory(uuid="5c5f67b9-e63c-6297-80da-000000000009", playbook=playbook)
        # Default gets a different uuid
        factories.TaskFactory(playbook=playbook)

        # Query for the first task uuid and expect one result
        request = self.client.get("/api/v1/tasks?uuid=%s" % task.uuid)
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(task.uuid, request.data["results"][0]["uuid"])

    def test_get_task_duration(self):
        started = timezone.now()
        ended = started + datetime.timedelta(hours=1)
        task = factories.TaskFactory(started=started, ended=ended)
        request = self.client.get("/api/v1/tasks/%s" % task.id)
        self.assertEqual(parse_duration(request.data["duration"]), ended - started)

    def test_get_task_by_date(self):
        task = factories.TaskFactory()

        past = datetime.datetime.now() - datetime.timedelta(hours=12)
        negative_date_fields = ["created_before", "started_before", "updated_before"]
        positive_date_fields = ["created_after", "started_after", "updated_after"]

        # Expect no task when searching before it was created
        for field in negative_date_fields:
            request = self.client.get("/api/v1/tasks?%s=%s" % (field, past.isoformat()))
            self.assertEqual(request.data["count"], 0)

        # Expect a task when searching after it was created
        for field in positive_date_fields:
            request = self.client.get("/api/v1/tasks?%s=%s" % (field, past.isoformat()))
            self.assertEqual(request.data["count"], 1)
            self.assertEqual(request.data["results"][0]["id"], task.id)

    def test_get_task_order(self):
        old_started = timezone.now() - datetime.timedelta(hours=12)
        old_ended = old_started + datetime.timedelta(minutes=30)
        old_task = factories.TaskFactory(started=old_started, ended=old_ended)
        new_started = timezone.now() - datetime.timedelta(hours=6)
        new_ended = new_started + datetime.timedelta(hours=1)
        new_task = factories.TaskFactory(started=new_started, ended=new_ended)

        # Ensure we have two objects
        request = self.client.get("/api/v1/tasks")
        self.assertEqual(2, len(request.data["results"]))

        order_fields = ["id", "created", "updated", "started", "ended", "duration"]
        # Ascending order
        for field in order_fields:
            request = self.client.get("/api/v1/tasks?order=%s" % field)
            self.assertEqual(request.data["results"][0]["id"], old_task.id)

        # Descending order
        for field in order_fields:
            request = self.client.get("/api/v1/tasks?order=-%s" % field)
            self.assertEqual(request.data["results"][0]["id"], new_task.id)

    def test_update_wrong_task_status(self):
        task = factories.TaskFactory()
        self.assertNotEqual("wrong", task.status)
        request = self.client.patch("/api/v1/tasks/%s" % task.id, {"status": "wrong"})
        self.assertEqual(400, request.status_code)
        task_updated = models.Task.objects.get(id=task.id)
        self.assertNotEqual("wrong", task_updated.status)

    def test_get_task_by_status(self):
        task = factories.TaskFactory(status="running")
        factories.TaskFactory(status="completed")
        factories.TaskFactory(status="unknown")
        factories.TaskFactory(status="failed")

        # Confirm we have four tasks
        request = self.client.get("/api/v1/tasks")
        self.assertEqual(4, len(request.data["results"]))

        # Test single status
        request = self.client.get("/api/v1/tasks?status=running")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(task.status, request.data["results"][0]["status"])

        # Test multiple status
        request = self.client.get("/api/v1/tasks?status=running&status=completed")
        self.assertEqual(2, len(request.data["results"]))

    def test_get_task_by_action(self):
        task = factories.TaskFactory(action="debug")
        factories.TaskFactory(action="setup")

        # Confirm we have two objects
        request = self.client.get("/api/v1/tasks")
        self.assertEqual(2, len(request.data["results"]))

        # Expect the correct single result when searching
        request = self.client.get("/api/v1/tasks?action=debug")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(task.id, request.data["results"][0]["id"])
        self.assertEqual(task.action, request.data["results"][0]["action"])

    def test_get_task_by_path(self):
        # Create two files with different paths
        first_file = factories.FileFactory(path="/root/roles/foo/tasks/main.yml")
        second_file = factories.FileFactory(path="/root/roles/bar/tasks/main.yml")

        # Create two tasks using these files
        task = factories.TaskFactory(file=first_file)
        factories.TaskFactory(file=second_file)

        # Test exact match
        request = self.client.get("/api/v1/tasks?path=/root/roles/foo/tasks/main.yml")
        self.assertEqual(1, len(request.data["results"]))
        self.assertEqual(task.file.path, request.data["results"][0]["path"])

        # Test partial match
        request = self.client.get("/api/v1/tasks?path=main.yml")
        self.assertEqual(len(request.data["results"]), 2)

    def test_get_playbook_arguments(self):
        task = factories.TaskFactory()
        request = self.client.get("/api/v1/tasks/%s" % task.id)
        self.assertIn("inventory", request.data["playbook"]["arguments"])
