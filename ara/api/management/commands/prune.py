import logging
import sys
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from ara.clients.utils import get_client

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Deletes playbooks from the database based on their age"
    deleted = 0

    def add_arguments(self, parser):
        parser.add_argument(
            "--client",
            type=str,
            default="offline",
            help="API client to use for the query: 'offline' or 'http' (default: 'offline')",
        )
        parser.add_argument(
            "--endpoint",
            type=str,
            default="http://127.0.0.1:8000",
            help="API endpoint to use for the query (default: 'http://127.0.0.1:8000')",
        )
        parser.add_argument(
            "--username", type=str, default=None, help="API username to use for the query (default: None)"
        )
        parser.add_argument(
            "--password", type=str, default=None, help="API password to use for the query (default: None)"
        )
        parser.add_argument("--insecure", action="store_true", help="Disables SSL certificate validation")
        parser.add_argument("--timeout", type=int, default=10, help="Timeout for API queries (default: 10)")
        parser.add_argument(
            "--days", type=int, default=31, help="Delete playbooks started this many days ago (default: 31)"
        )
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Confirm deletion of playbooks, otherwise runs without deleting any playbook",
        )

    def handle(self, *args, **options):
        client = options.get("client")
        endpoint = options.get("endpoint")
        username = options.get("username")
        password = options.get("password")
        insecure = options.get("insecure")
        timeout = options.get("timeout")
        days = options.get("days")
        confirm = options.get("confirm")

        # Get an instance of either an offline or http client with the specified parameters.
        # When using the offline client, don't run SQL migrations.
        api_client = get_client(
            client=client,
            endpoint=endpoint,
            username=username,
            password=password,
            verify=False if insecure else True,
            timeout=timeout,
            run_sql_migrations=False,
        )

        if not confirm:
            logger.info("--confirm was not specified, no playbooks will be deleted")

        # generate a timestamp from n days ago in a format we can query the API with
        # ex: 2019-11-21T00:57:41.702229
        limit_date = (datetime.now() - timedelta(days=days)).isoformat()

        logger.info("Querying %s/api/v1/playbooks/?started_before=%s" % (endpoint, limit_date))
        playbooks = api_client.get("/api/v1/playbooks", started_before=limit_date)

        # TODO: Improve client validation and exception handling
        if "count" not in playbooks:
            # If we didn't get an answer we can parse, it's probably due to an error 500, 403, 401, etc.
            # The client would have logged the error.
            logger.error("Client failed to retrieve results, see logs for ara.clients.offline or ara.clients.http.")
            sys.exit(1)

        logger.info("Found %s playbooks matching query" % playbooks["count"])

        for playbook in playbooks["results"]:
            if not confirm:
                msg = "Dry-run: playbook {id} ({path}) would have been deleted, start date: {started}"
                logger.info(msg.format(id=playbook["id"], path=playbook["path"], started=playbook["started"]))
            else:
                msg = "Deleting playbook {id} ({path}), start date: {started}"
                logger.info(msg.format(id=playbook["id"], path=playbook["path"], started=playbook["started"]))
                api_client.delete("/api/v1/playbooks/%s" % playbook["id"])
                self.deleted += 1

        logger.info("%s playbooks deleted" % self.deleted)
