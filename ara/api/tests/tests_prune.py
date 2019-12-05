import datetime
from unittest import skip

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import LiveServerTestCase, TestCase, override_settings

from ara.api import models
from ara.api.tests import factories


class LogCheckerMixin(object):
    def run_prune_command(self, *args, **opts):
        # the command uses logging instead of prints so we need to use assertLogs
        # to retrieve and test the output
        with self.assertLogs("ara.api.management.commands.prune", "INFO") as logs:
            call_command("prune", *args, **opts)
            return logs.output


class PruneTestCase(TestCase, LogCheckerMixin):
    @skip("TODO: Why aren't logs captured properly for this test ?")
    def test_prune_without_playbooks_and_confirm(self):
        output = self.run_prune_command()
        self.assertIn(
            "INFO:ara.api.management.commands.prune:--confirm was not specified, no playbooks will be deleted", output
        )
        self.assertIn("INFO:ara.api.management.commands.prune:Found 0 playbooks matching query", output)
        self.assertIn("INFO:ara.api.management.commands.prune:0 playbooks deleted", output)

    @skip("TODO: Why aren't logs captured properly for this test ?")
    def test_prune_without_playbooks(self):
        args = ["--confirm"]
        output = self.run_prune_command(*args)
        self.assertNotIn(
            "INFO:ara.api.management.commands.prune:--confirm was not specified, no playbooks will be deleted", output
        )
        self.assertIn("INFO:ara.api.management.commands.prune:Found 0 playbooks matching query", output)
        self.assertIn("INFO:ara.api.management.commands.prune:0 playbooks deleted", output)


class PruneCmdTestCase(LiveServerTestCase, LogCheckerMixin):
    @skip("TODO: Why aren't logs captured properly for this test ?")
    def test_prune_with_no_matching_playbook(self):
        # Create a playbook with start date as of now
        factories.PlaybookFactory()
        self.assertEqual(1, models.Playbook.objects.all().count())

        args = ["--confirm"]
        output = self.run_prune_command(*args)
        self.assertIn("INFO:ara.api.management.commands.prune:Found 0 playbooks matching query", output)
        self.assertIn("INFO:ara.api.management.commands.prune:0 playbooks deleted", output)
        self.assertEqual(1, models.Playbook.objects.all().count())

    @skip("TODO: Why aren't logs captured properly for this test ?")
    def test_prune_with_matching_playbook(self):
        # Create a playbook with an old start date
        old_timestamp = datetime.datetime.now() - datetime.timedelta(days=60)
        factories.PlaybookFactory(started=old_timestamp)
        self.assertEqual(1, models.Playbook.objects.all().count())

        args = ["--confirm"]
        output = self.run_prune_command(*args)
        self.assertIn("INFO:ara.api.management.commands.prune:Found 1 playbooks matching query", output)
        self.assertIn("INFO:ara.api.management.commands.prune:1 playbooks deleted", output)
        self.assertEqual(0, models.Playbook.objects.all().count())

    def test_prune_with_no_matching_playbook_with_http_client(self):
        # Create a playbook with start date as of now
        factories.PlaybookFactory()
        self.assertEqual(1, models.Playbook.objects.all().count())

        args = ["--confirm", "--client", "http", "--endpoint", self.live_server_url]
        output = self.run_prune_command(*args)
        self.assertIn("INFO:ara.api.management.commands.prune:Found 0 playbooks matching query", output)
        self.assertIn("INFO:ara.api.management.commands.prune:0 playbooks deleted", output)
        self.assertEqual(1, models.Playbook.objects.all().count())

    def test_prune_with_matching_playbook_with_http_client(self):
        # Create a playbook with an old start date
        old_timestamp = datetime.datetime.now() - datetime.timedelta(days=60)
        factories.PlaybookFactory(started=old_timestamp)
        self.assertEqual(1, models.Playbook.objects.all().count())

        args = ["--confirm", "--client", "http", "--endpoint", self.live_server_url]
        output = self.run_prune_command(*args)
        self.assertIn("INFO:ara.api.management.commands.prune:Found 1 playbooks matching query", output)
        self.assertIn("INFO:ara.api.management.commands.prune:1 playbooks deleted", output)
        self.assertEqual(0, models.Playbook.objects.all().count())

    @override_settings(READ_LOGIN_REQUIRED=True, WRITE_LOGIN_REQUIRED=True)
    def test_prune_without_authenticated_http_client(self):
        args = ["--confirm", "--client", "http", "--endpoint", self.live_server_url]
        with self.assertRaises(SystemExit):
            self.run_prune_command(*args)

    @override_settings(READ_LOGIN_REQUIRED=True, WRITE_LOGIN_REQUIRED=True)
    def test_prune_with_authenticated_http_client(self):
        # Create a user
        self.user = User.objects.create_superuser("prune", "prune@example.org", "password")

        # Create a playbook with an old start date
        old_timestamp = datetime.datetime.now() - datetime.timedelta(days=60)
        factories.PlaybookFactory(started=old_timestamp)
        self.assertEqual(1, models.Playbook.objects.all().count())

        args = [
            "--confirm",
            "--client",
            "http",
            "--endpoint",
            self.live_server_url,
            "--username",
            "prune",
            "--password",
            "password",
        ]
        output = self.run_prune_command(*args)
        self.assertIn("INFO:ara.api.management.commands.prune:Found 1 playbooks matching query", output)
        self.assertIn("INFO:ara.api.management.commands.prune:1 playbooks deleted", output)
        self.assertEqual(0, models.Playbook.objects.all().count())

    @override_settings(READ_LOGIN_REQUIRED=True, WRITE_LOGIN_REQUIRED=True)
    def test_prune_with_bad_authentication_http_client(self):
        # Create a user
        self.user = User.objects.create_superuser("prune", "prune@example.org", "password")

        # Create a playbook with an old start date
        old_timestamp = datetime.datetime.now() - datetime.timedelta(days=60)
        factories.PlaybookFactory(started=old_timestamp)
        self.assertEqual(1, models.Playbook.objects.all().count())

        # Set up arguments with a wrong password
        args = [
            "--confirm",
            "--client",
            "http",
            "--endpoint",
            self.live_server_url,
            "--username",
            "prune",
            "--password",
            "somethingelse",
        ]

        with self.assertRaises(SystemExit):
            self.run_prune_command(*args)
            # TODO: the assertRaises prevents us from looking at the output
            # output = run_prune_command(*args)
            # self.assertIn("Client failed to retrieve results, see logs for ara.clients.offline or ara.clients.http.", output)  # noqa

        # Nothing should have been deleted because the command failed
        self.assertEqual(1, models.Playbook.objects.all().count())
