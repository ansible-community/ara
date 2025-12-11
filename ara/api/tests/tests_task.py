# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import datetime

from django.utils import timezone
from django.utils.dateparse import parse_duration
from rest_framework.test import APITestCase

from ara.api import models, serializers
from ara.api.tests import factories, utils

# Sample data for testing deprecations, exceptions, and warnings
TASK_DEPRECATIONS = [
    {
        "collection_name": "ansible.builtin",
        "msg": "The internal 'vars' dictionary is deprecated.",
        "version": "2.24",
        "deprecator": {"resolved_name": "ansible.builtin"},
    },
    {
        "collection_name": "community.general",
        "msg": "This module is deprecated, use the new module instead.",
        "version": "3.0.0",
        "deprecator": {"resolved_name": "community.general"},
    },
]

TASK_EXCEPTIONS = [
    'Traceback (most recent call last):\n  File "<string>", line 1\nRuntimeError: Something went wrong',
    'Traceback (most recent call last):\n  File "test.py", line 42\nValueError: Invalid value',
]

TASK_WARNINGS = [
    "Platform linux on host localhost is using the discovered Python interpreter",
    "Skipping plugin, did not meet requirements",
    "Module did not set no_log for sensitive_field",
]


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


class TaskNotesTestCase(APITestCase):
    """Tests for task deprecations, exceptions, and warnings fields."""

    def test_task_factory_with_warnings(self):
        """Test that TaskFactory can create tasks with warnings."""
        task = factories.TaskFactory(warnings=TASK_WARNINGS)
        self.assertEqual(task.warnings, TASK_WARNINGS)

    def test_task_factory_with_deprecations(self):
        """Test that TaskFactory can create tasks with deprecations."""
        task = factories.TaskFactory(deprecations=TASK_DEPRECATIONS)
        self.assertEqual(task.deprecations, TASK_DEPRECATIONS)

    def test_task_factory_with_exceptions(self):
        """Test that TaskFactory can create tasks with exceptions."""
        task = factories.TaskFactory(exceptions=TASK_EXCEPTIONS)
        self.assertEqual(task.exceptions, TASK_EXCEPTIONS)

    def test_task_factory_default_empty_lists(self):
        """Test that TaskFactory creates tasks with empty lists by default."""
        task = factories.TaskFactory()
        self.assertEqual(task.warnings, [])
        self.assertEqual(task.deprecations, [])
        self.assertEqual(task.exceptions, [])

    def test_task_serializer_with_warnings(self):
        """Test that the serializer properly handles warnings."""
        play = factories.PlayFactory()
        file = factories.FileFactory()
        serializer = serializers.TaskSerializer(
            data={
                "name": "task_with_warnings",
                "uuid": "5c5f67b9-e63c-6297-80da-000000000010",
                "action": "debug",
                "lineno": 5,
                "status": "completed",
                "handler": False,
                "play": play.id,
                "file": file.id,
                "playbook": play.playbook.id,
                "warnings": TASK_WARNINGS,
            }
        )
        serializer.is_valid()
        task = serializer.save()
        task.refresh_from_db()
        self.assertEqual(task.warnings, TASK_WARNINGS)

    def test_task_serializer_with_deprecations(self):
        """Test that the serializer properly handles deprecations."""
        play = factories.PlayFactory()
        file = factories.FileFactory()
        serializer = serializers.TaskSerializer(
            data={
                "name": "task_with_deprecations",
                "uuid": "5c5f67b9-e63c-6297-80da-000000000011",
                "action": "debug",
                "lineno": 10,
                "status": "completed",
                "handler": False,
                "play": play.id,
                "file": file.id,
                "playbook": play.playbook.id,
                "deprecations": TASK_DEPRECATIONS,
            }
        )
        serializer.is_valid()
        task = serializer.save()
        task.refresh_from_db()
        self.assertEqual(task.deprecations, TASK_DEPRECATIONS)

    def test_task_serializer_with_exceptions(self):
        """Test that the serializer properly handles exceptions."""
        play = factories.PlayFactory()
        file = factories.FileFactory()
        serializer = serializers.TaskSerializer(
            data={
                "name": "task_with_exceptions",
                "uuid": "5c5f67b9-e63c-6297-80da-000000000012",
                "action": "command",
                "lineno": 15,
                "status": "failed",
                "handler": False,
                "play": play.id,
                "file": file.id,
                "playbook": play.playbook.id,
                "exceptions": TASK_EXCEPTIONS,
            }
        )
        serializer.is_valid()
        task = serializer.save()
        task.refresh_from_db()
        self.assertEqual(task.exceptions, TASK_EXCEPTIONS)

    def test_task_serializer_output_includes_notes_fields(self):
        """Test that serializer output includes warnings, deprecations, and exceptions."""
        task = factories.TaskFactory(
            warnings=TASK_WARNINGS,
            deprecations=TASK_DEPRECATIONS,
            exceptions=TASK_EXCEPTIONS,
        )
        serializer = serializers.TaskSerializer(instance=task)
        self.assertEqual(serializer.data["warnings"], TASK_WARNINGS)
        self.assertEqual(serializer.data["deprecations"], TASK_DEPRECATIONS)
        self.assertEqual(serializer.data["exceptions"], TASK_EXCEPTIONS)

    def test_create_task_with_notes_via_api(self):
        """Test creating a task with notes fields via the API."""
        play = factories.PlayFactory()
        file = factories.FileFactory()
        self.assertEqual(0, models.Task.objects.count())
        request = self.client.post(
            "/api/v1/tasks",
            {
                "name": "create_with_notes",
                "uuid": "5c5f67b9-e63c-6297-80da-000000000013",
                "action": "debug",
                "lineno": 20,
                "handler": False,
                "status": "completed",
                "play": play.id,
                "file": file.id,
                "playbook": play.playbook.id,
                "warnings": TASK_WARNINGS,
                "deprecations": TASK_DEPRECATIONS,
                "exceptions": TASK_EXCEPTIONS,
            },
            format="json",
        )
        self.assertEqual(201, request.status_code)
        self.assertEqual(1, models.Task.objects.count())
        task = models.Task.objects.first()
        self.assertEqual(task.warnings, TASK_WARNINGS)
        self.assertEqual(task.deprecations, TASK_DEPRECATIONS)
        self.assertEqual(task.exceptions, TASK_EXCEPTIONS)

    def test_get_task_with_notes(self):
        """Test retrieving a task with notes fields via the API."""
        task = factories.TaskFactory(
            warnings=TASK_WARNINGS,
            deprecations=TASK_DEPRECATIONS,
            exceptions=TASK_EXCEPTIONS,
        )
        request = self.client.get("/api/v1/tasks/%s" % task.id)
        self.assertEqual(200, request.status_code)
        self.assertEqual(request.data["warnings"], TASK_WARNINGS)
        self.assertEqual(request.data["deprecations"], TASK_DEPRECATIONS)
        self.assertEqual(request.data["exceptions"], TASK_EXCEPTIONS)

    def test_get_tasks_list_includes_notes(self):
        """Test that the tasks list endpoint includes notes fields."""
        factories.TaskFactory(
            name="task_with_notes",
            warnings=TASK_WARNINGS,
            deprecations=TASK_DEPRECATIONS,
            exceptions=TASK_EXCEPTIONS,
        )
        request = self.client.get("/api/v1/tasks")
        self.assertEqual(1, len(request.data["results"]))
        result = request.data["results"][0]
        self.assertEqual(result["warnings"], TASK_WARNINGS)
        self.assertEqual(result["deprecations"], TASK_DEPRECATIONS)
        self.assertEqual(result["exceptions"], TASK_EXCEPTIONS)

    def test_partial_update_task_warnings(self):
        """Test partial update of task warnings via the API."""
        task = factories.TaskFactory(warnings=[])
        self.assertEqual([], task.warnings)
        request = self.client.patch(
            "/api/v1/tasks/%s" % task.id,
            {"warnings": TASK_WARNINGS},
            format="json",
        )
        self.assertEqual(200, request.status_code)
        task_updated = models.Task.objects.get(id=task.id)
        self.assertEqual(TASK_WARNINGS, task_updated.warnings)

    def test_partial_update_task_deprecations(self):
        """Test partial update of task deprecations via the API."""
        task = factories.TaskFactory(deprecations=[])
        self.assertEqual([], task.deprecations)
        request = self.client.patch(
            "/api/v1/tasks/%s" % task.id,
            {"deprecations": TASK_DEPRECATIONS},
            format="json",
        )
        self.assertEqual(200, request.status_code)
        task_updated = models.Task.objects.get(id=task.id)
        self.assertEqual(TASK_DEPRECATIONS, task_updated.deprecations)

    def test_partial_update_task_exceptions(self):
        """Test partial update of task exceptions via the API."""
        task = factories.TaskFactory(exceptions=[])
        self.assertEqual([], task.exceptions)
        request = self.client.patch(
            "/api/v1/tasks/%s" % task.id,
            {"exceptions": TASK_EXCEPTIONS},
            format="json",
        )
        self.assertEqual(200, request.status_code)
        task_updated = models.Task.objects.get(id=task.id)
        self.assertEqual(TASK_EXCEPTIONS, task_updated.exceptions)

    def test_task_with_single_warning(self):
        """Test task with a single warning."""
        single_warning = ["This is a single warning message"]
        task = factories.TaskFactory(warnings=single_warning)
        request = self.client.get("/api/v1/tasks/%s" % task.id)
        self.assertEqual(request.data["warnings"], single_warning)
        self.assertEqual(len(request.data["warnings"]), 1)

    def test_task_with_single_deprecation(self):
        """Test task with a single deprecation."""
        single_deprecation = [TASK_DEPRECATIONS[0]]
        task = factories.TaskFactory(deprecations=single_deprecation)
        request = self.client.get("/api/v1/tasks/%s" % task.id)
        self.assertEqual(request.data["deprecations"], single_deprecation)
        self.assertEqual(len(request.data["deprecations"]), 1)

    def test_task_with_single_exception(self):
        """Test task with a single exception."""
        single_exception = [TASK_EXCEPTIONS[0]]
        task = factories.TaskFactory(exceptions=single_exception)
        request = self.client.get("/api/v1/tasks/%s" % task.id)
        self.assertEqual(request.data["exceptions"], single_exception)
        self.assertEqual(len(request.data["exceptions"]), 1)

    def test_task_notes_preserved_on_status_update(self):
        """Test that notes fields are preserved when updating task status."""
        task = factories.TaskFactory(
            status="running",
            warnings=TASK_WARNINGS,
            deprecations=TASK_DEPRECATIONS,
            exceptions=TASK_EXCEPTIONS,
        )
        request = self.client.patch(
            "/api/v1/tasks/%s" % task.id,
            {"status": "completed"},
            format="json",
        )
        self.assertEqual(200, request.status_code)
        task_updated = models.Task.objects.get(id=task.id)
        self.assertEqual("completed", task_updated.status)
        # Verify notes are preserved
        self.assertEqual(TASK_WARNINGS, task_updated.warnings)
        self.assertEqual(TASK_DEPRECATIONS, task_updated.deprecations)
        self.assertEqual(TASK_EXCEPTIONS, task_updated.exceptions)

    def test_task_with_unicode_in_warnings(self):
        """Test task with unicode characters in warnings."""
        unicode_warnings = ["Warning: 日本語テスト", "Warning: émojis 🚀 included"]
        task = factories.TaskFactory(warnings=unicode_warnings)
        request = self.client.get("/api/v1/tasks/%s" % task.id)
        self.assertEqual(request.data["warnings"], unicode_warnings)

    def test_get_tasks_by_playbook_includes_notes(self):
        """Test that filtering tasks by playbook includes notes fields."""
        playbook = factories.PlaybookFactory()
        factories.TaskFactory(
            name="task_with_notes",
            playbook=playbook,
            warnings=TASK_WARNINGS,
            deprecations=TASK_DEPRECATIONS,
        )
        request = self.client.get("/api/v1/tasks?playbook=%s" % playbook.id)
        self.assertEqual(1, len(request.data["results"]))
        result = request.data["results"][0]
        self.assertEqual(result["warnings"], TASK_WARNINGS)
        self.assertEqual(result["deprecations"], TASK_DEPRECATIONS)

    def test_delete_task_with_notes(self):
        """Test deleting a task that has notes fields."""
        task = factories.TaskFactory(
            warnings=TASK_WARNINGS,
            deprecations=TASK_DEPRECATIONS,
            exceptions=TASK_EXCEPTIONS,
        )
        self.assertEqual(1, models.Task.objects.all().count())
        request = self.client.delete("/api/v1/tasks/%s" % task.id)
        self.assertEqual(204, request.status_code)
        self.assertEqual(0, models.Task.objects.all().count())

    def test_clear_task_notes(self):
        """Test clearing notes fields by setting them to empty lists."""
        task = factories.TaskFactory(
            warnings=TASK_WARNINGS,
            deprecations=TASK_DEPRECATIONS,
            exceptions=TASK_EXCEPTIONS,
        )
        request = self.client.patch(
            "/api/v1/tasks/%s" % task.id,
            {"warnings": [], "deprecations": [], "exceptions": []},
            format="json",
        )
        self.assertEqual(200, request.status_code)
        task_updated = models.Task.objects.get(id=task.id)
        self.assertEqual([], task_updated.warnings)
        self.assertEqual([], task_updated.deprecations)
        self.assertEqual([], task_updated.exceptions)

    def test_filter_tasks_by_deprecations_gt(self):
        """deprecations_count__gt=0 should return only tasks with deprecations."""
        # An ordinary task
        factories.TaskFactory(name="ordinary")
        # A task with deprecations
        task = factories.TaskFactory(name="deprecated", deprecations=TASK_DEPRECATIONS)

        resp = self.client.get("/api/v1/tasks?deprecations_count__gt=0")
        self.assertEqual(200, resp.status_code)
        ids = {r["id"] for r in resp.data["results"]}
        # We should only have the task with a deprecation
        self.assertEqual(len(ids), 1)
        self.assertIn(task.id, ids)

    def test_filter_tasks_by_exceptions_gt(self):
        """exceptions_count__gt=0 should return only tasks with exceptions."""
        # An ordinary task
        factories.TaskFactory(name="ordinary")
        # A task with exceptions
        task = factories.TaskFactory(name="excepted", exceptions=TASK_EXCEPTIONS)

        resp = self.client.get("/api/v1/tasks?exceptions_count__gt=0")
        self.assertEqual(200, resp.status_code)
        ids = {r["id"] for r in resp.data["results"]}
        # We should only have the task with an exception
        self.assertEqual(len(ids), 1)
        self.assertIn(task.id, ids)

    def test_filter_tasks_by_warnings_gt(self):
        """warnings_count__gt=0 should return only tasks with warnings."""
        # An ordinary task
        factories.TaskFactory(name="ordinary")
        # A task with warnings
        task = factories.TaskFactory(name="warned", warnings=TASK_WARNINGS)

        resp = self.client.get("/api/v1/tasks?warnings_count__gt=0")
        self.assertEqual(200, resp.status_code)
        ids = {r["id"] for r in resp.data["results"]}
        # We should only have the task with a warning
        self.assertEqual(len(ids), 1)
        self.assertIn(task.id, ids)

    def test_filter_tasks_by_deprecations_lt(self):
        """deprecations_count__lt=1 shouldn't return tasks with deprecations."""
        # An ordinary task
        task = factories.TaskFactory(name="ordinary")
        # A task with deprecations
        factories.TaskFactory(name="deprecated", deprecations=TASK_DEPRECATIONS)

        resp = self.client.get("/api/v1/tasks?deprecations_count__lt=1")
        self.assertEqual(200, resp.status_code)
        ids = {r["id"] for r in resp.data["results"]}
        # We should only have the task without a deprecation
        self.assertEqual(len(ids), 1)
        self.assertIn(task.id, ids)

    def test_filter_tasks_by_exceptions_lt(self):
        """exceptions_count__lt=1 shouldn't return tasks with exceptions."""
        # An ordinary task
        task = factories.TaskFactory(name="ordinary")
        # A task with exceptions
        factories.TaskFactory(name="excepted", exceptions=TASK_EXCEPTIONS)

        resp = self.client.get("/api/v1/tasks?exceptions_count__lt=1")
        self.assertEqual(200, resp.status_code)
        ids = {r["id"] for r in resp.data["results"]}
        # We should only have the task without an exception
        self.assertEqual(len(ids), 1)
        self.assertIn(task.id, ids)

    def test_filter_tasks_by_warnings_lt(self):
        """warnings_count__lt=1 shouldn't return tasks with warnings."""
        # An ordinary task
        task = factories.TaskFactory(name="ordinary")
        # A task with warnings
        factories.TaskFactory(name="warned", warnings=TASK_WARNINGS)

        resp = self.client.get("/api/v1/tasks?warnings_count__lt=1")
        self.assertEqual(200, resp.status_code)
        ids = {r["id"] for r in resp.data["results"]}
        # We should only have the task without a warning
        self.assertEqual(len(ids), 1)
        self.assertIn(task.id, ids)

    def test_filter_tasks_by_multiple_counts(self):
        """Combination filters (e.g. warnings & exceptions) should AND together."""
        # Task with both warning and exception
        task = factories.TaskFactory(
            name="mixed",
            exceptions=TASK_EXCEPTIONS,
            warnings=TASK_WARNINGS,
        )
        # Pure warning task should be excluded by the “exceptions” part
        factories.TaskFactory(name="only_warn", warnings=TASK_WARNINGS)

        resp = self.client.get("/api/v1/tasks?warnings_count__gt=0&exceptions_count__gt=0")
        self.assertEqual(200, resp.status_code)
        ids = {r["id"] for r in resp.data["results"]}
        # We should only have the task with the exception
        self.assertEqual(len(ids), 1)
        self.assertIn(task.id, ids)
