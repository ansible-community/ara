# Copyright (c) 2023 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
import sys
import time
from collections import defaultdict
from datetime import datetime, timedelta

from cliff.command import Command

import ara.cli.utils as cli_utils
from ara.cli.base import global_arguments
from ara.clients.utils import get_client

try:
    from prometheus_client import Gauge, Summary, start_http_server

    HAS_PROMETHEUS_CLIENT = True
except ImportError:
    HAS_PROMETHEUS_CLIENT = False

# Where possible and relevant, apply these labels to the metrics so we can write prometheus
# queries to filter and aggregate by these properties
# TODO: make configurable
DEFAULT_PLAYBOOK_LABELS = [
    "ansible_version",
    "client_version",
    "controller",
    "name",
    "path",
    "python_version",
    "server_version",
    "status",
    "updated",
    "user",
]
DEFAULT_TASK_LABELS = ["action", "name", "path", "playbook", "status", "updated"]
DEFAULT_HOST_LABELS = ["name", "playbook", "updated"]


# TODO: This method should be more flexible and live in a library
def get_search_results(client, kind, limit, created_after):
    """
    kind: string, one of ["playbooks", "hosts", "tasks"]
    limit: int, the number of items to return per page
    created_after: string, a date formatted as such: 2020-01-31T15:45:36.737000Z
    """
    query = f"/api/v1/{kind}?order=-id&limit={limit}"
    if created_after is not None:
        query += f"&created_after={created_after}"

    response = client.get(query)
    items = response["results"]

    # Iterate through multiple pages of results if necessary
    while response["next"]:
        # For example:
        # "next": "https://demo.recordsansible.org/api/v1/playbooks?limit=1000&offset=2000",
        uri = response["next"].replace(client.endpoint, "")
        response = client.get(uri)
        items.extend(response["results"])

    return items


class AraPlaybookCollector(object):
    def __init__(self, client, log, limit, labels=DEFAULT_PLAYBOOK_LABELS):
        self.client = client
        self.log = log
        self.limit = limit
        self.labels = labels

        self.metrics = {
            "completed": Gauge("ara_playbooks_completed", "Completed Ansible playbooks", labels),
            "expired": Gauge("ara_playbooks_expired", "Expired Ansible playbooks", labels),
            "failed": Gauge("ara_playbooks_failed", "Failed Ansible playbooks", labels),
            "range": Gauge("ara_playbooks_range", "Limit metric collection to the N most recent playbooks"),
            "running": Gauge("ara_playbooks_running", "Running Ansible playbooks", labels),
            "total": Gauge("ara_playbooks_total", "Total number of playbooks recorded by ara"),
            "duration": Summary("ara_playbooks_duration", "Duration (in seconds) of playbooks recorded by ara", labels),
        }

    def collect_metrics(self, created_after=None, limit=1000):
        self.metrics["range"].set(limit)

        playbooks = get_search_results(self.client, "playbooks", self.limit, created_after)
        # Save the most recent timestamp so we only scrape beyond it next time
        if playbooks:
            created_after = cli_utils.increment_timestamp(playbooks[0]["created"])
            self.log.info(f"updating metrics for {len(playbooks)} playbooks...")

        for playbook in playbooks:
            self.metrics["total"].inc()

            # Gather the values of each label so we can attach them to our metrics
            labels = {label: playbook[label] for label in self.labels}
            self.metrics[playbook["status"]].labels(**labels).inc()

            # The API returns a duration in string format, convert it back to seconds
            # so we can use it as a value for the metric.
            if playbook["duration"] is not None:
                # TODO: parse_timedelta throws an exception for playbooks that last longer than a day
                # That was meant to be fixed in https://github.com/ansible-community/ara/commit/db8243c3af938ece12c9cd59dd7fe4d9a711b76d
                try:
                    seconds = cli_utils.parse_timedelta(playbook["duration"])
                except ValueError:
                    seconds = 0
            else:
                seconds = 0
            self.metrics["duration"].labels(**labels).observe(seconds)

        return created_after


class AraTaskCollector(object):
    def __init__(self, client, log, limit, labels=DEFAULT_TASK_LABELS):
        self.client = client
        self.log = log
        self.limit = limit
        self.labels = labels

        self.metrics = {
            "completed": Gauge("ara_tasks_completed", "Completed Ansible tasks", labels),
            "expired": Gauge("ara_tasks_expired", "Expired Ansible tasks", labels),
            "failed": Gauge("ara_tasks_failed", "Failed Ansible tasks", labels),
            "range": Gauge("ara_tasks_range", "Limit metric collection to the N most recent tasks"),
            "running": Gauge("ara_tasks_running", "Running Ansible tasks", labels),
            "total": Gauge("ara_tasks_total", "Number of tasks recorded by ara in prometheus"),
            "duration": Summary(
                "ara_tasks_duration", "Duration, in seconds, of playbook tasks recorded by ara", labels
            ),
        }

    def collect_metrics(self, created_after=None):
        self.metrics["range"].set(self.limit)

        tasks = get_search_results(self.client, "tasks", self.limit, created_after)
        # Save the most recent timestamp so we only scrape beyond it next time
        if tasks:
            created_after = cli_utils.increment_timestamp(tasks[0]["created"])
            self.log.info(f"updating metrics for {len(tasks)} tasks...")

        for task in tasks:
            self.metrics["total"].inc()

            # Gather the values of each label so we can attach them to our metrics
            labels = {label: task[label] for label in self.labels}
            self.metrics[task["status"]].labels(**labels).inc()

            # The API returns a duration in string format, convert it back to seconds
            # so we can use it as a value for the metric.
            if task["duration"] is not None:
                # TODO: parse_timedelta throws an exception for tasks that last longer than a day
                # That was meant to be fixed in https://github.com/ansible-community/ara/commit/db8243c3af938ece12c9cd59dd7fe4d9a711b76d
                try:
                    seconds = cli_utils.parse_timedelta(task["duration"])
                except ValueError:
                    seconds = 0
            else:
                seconds = 0
            self.metrics["duration"].labels(**labels).observe(seconds)

        return created_after


class AraHostCollector(object):
    def __init__(self, client, log, limit, labels=DEFAULT_HOST_LABELS):
        self.client = client
        self.log = log
        self.limit = limit
        self.labels = labels

        self.metrics = {
            "changed": Gauge("ara_hosts_changed", "Number of changes on a host", labels),
            "failed": Gauge("ara_hosts_failed", "Number of failures on a host", labels),
            "ok": Gauge("ara_hosts_ok", "Number of successful tasks without changes on a host", labels),
            "range": Gauge("ara_hosts_range", "Limit metric collection to the N most recent hosts"),
            "skipped": Gauge("ara_hosts_skipped", "Number of skipped tasks on a host", labels),
            "total": Gauge("ara_hosts_total", "Hosts recorded by ara"),
            "unreachable": Gauge("ara_hosts_unreachable", "Number of unreachable errors on a host", labels),
        }

    def collect_metrics(self, created_after=None):
        self.metrics["range"].set(self.limit)

        hosts = get_search_results(self.client, "hosts", self.limit, created_after)
        # Save the most recent timestamp so we only scrape beyond it next time
        if hosts:
            created_after = cli_utils.increment_timestamp(hosts[0]["created"])
            self.log.info(f"updating metrics for {len(hosts)} hosts...")

        for host in hosts:
            self.metrics["total"].inc()

            # Gather the values of each label so we can attach them to our metrics
            labels = {label: host[label] for label in self.labels}

            # The values of "changed", "failed" and so on are integers so we can
            # use them as values for our metric
            for status in ["changed", "failed", "ok", "skipped", "unreachable"]:
                if host[status]:
                    self.metrics[status].labels(**labels).set(host[status])

        return created_after


class PrometheusExporter(Command):
    """Exposes a prometheus exporter to provide metrics from an instance of ara"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser = global_arguments(parser)
        # fmt: off
        parser.add_argument(
            '--playbook-limit',
            help='Max number of playbooks to request at once (default: 1000)',
            default=1000,
            type=int
        )
        parser.add_argument(
            '--task-limit',
            help='Max number of tasks to request at once (default: 2500)',
            default=2500,
            type=int
        )
        parser.add_argument(
            '--host-limit',
            help='Max number of hosts to request at once (default: 2500)',
            default=2500,
            type=int
        )
        parser.add_argument(
            '--poll-frequency',
            help='Seconds to wait until querying ara for new metrics (default: 60)',
            default=60,
            type=int
        )
        parser.add_argument(
            '--prometheus-port',
            help='Port on which the prometheus exporter will listen (default: 8001)',
            default=8001,
            type=int
        )
        parser.add_argument(
            '--max-days',
            help='Maximum number of days to backfill metrics for (default: 90)',
            default=90,
            type=int
        )
        return parser

    def take_action(self, args):
        if not HAS_PROMETHEUS_CLIENT:
            self.log.error("The prometheus_client python package must be installed to run this command")
            sys.exit(2)

        verify = False if args.insecure else True
        if args.ssl_ca:
            verify = args.ssl_ca
        client = get_client(
            client=args.client,
            endpoint=args.server,
            timeout=args.timeout,
            username=args.username,
            password=args.password,
            cert=args.ssl_cert,
            key=args.ssl_key,
            verify=verify,
            run_sql_migrations=False,
        )

        # Prepare collectors so we can gather various metrics
        playbooks = AraPlaybookCollector(client=client, log=self.log, limit=args.playbook_limit)
        hosts = AraHostCollector(client=client, log=self.log, limit=args.host_limit)
        tasks = AraTaskCollector(client=client, log=self.log, limit=args.task_limit)

        start_http_server(args.prometheus_port)
        self.log.info(f"ara prometheus exporter listening on http://0.0.0.0:{args.prometheus_port}/metrics")

        created_after = (datetime.now() - timedelta(days=args.max_days)).isoformat()
        self.log.info(
            f"Backfilling metrics for the last {args.max_days} days since {created_after}... This can take a while."
        )

        latest = defaultdict(lambda: created_after)
        while True:
            latest["playbooks"] = playbooks.collect_metrics(latest["playbooks"])
            latest["hosts"] = hosts.collect_metrics(latest["hosts"])
            latest["tasks"] = tasks.collect_metrics(latest["tasks"])

            time.sleep(args.poll_frequency)
            self.log.info("Checking for updated metrics...")
