# Copyright (c) 2023 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
import os
import sys
import time
from collections import defaultdict
from datetime import datetime, timedelta

from cliff.command import Command

import ara.cli.utils as cli_utils
from ara.cli.base import global_arguments
from ara.clients.utils import get_client

try:
    from prometheus_client import Gauge, Histogram, start_http_server
    HAS_PROMETHEUS_CLIENT = True
except ImportError:
    HAS_PROMETHEUS_CLIENT = False


class AraPlaybookCollector(object):
    def __init__(self, client, log):
        self.client = client
        self.log = log
        self.metrics = {
            "total": Gauge("ara_playbooks_total", "Total number of playbooks recorded by ara"),
            "range": Gauge("ara_playbooks_range", "Limit metric collection to the N most recent playbooks"),

            "playbooks": Histogram(
                "ara_playbooks",
                "Ansible playbooks recorded by ara",
                [
                    "timestamp",
                    "path",
                    "status",
                    "plays",
                    "tasks",
                    "results",
                    "hosts",
                    "files",
                    "records",
                    "ansible_version",
                    "python_version",
                    "client_version",
                    "server_version",
                ],
                buckets=(0.1, 1.0, 5.0, 10.0, 30.0, 60.0, 90.0, 120.0, 300.0, 600.0, 1200.0, 1800.0, 3600.0, float("inf"))
            ),
        }

    def collect_metrics(self, created_after=None, limit=1000):
        self.log.info("collecting playbook metrics...")
        self.metrics["range"].set(limit)

        if created_after is None:
            query = self.client.get(f"/api/v1/playbooks?order=-id&limit={limit}")
        else:
            query = self.client.get(f"/api/v1/playbooks?order=-id&limit={limit}&created_after={created_after}")
        playbooks = query["results"]

        # Iterate through multiple pages of results if necessary
        while query["next"]:
            # For example:
            # "next": "https://demo.recordsansible.org/api/v1/playbooks?limit=1000&offset=2000",
            uri = query["next"].replace(self.client.endpoint, "")
            query = self.client.get(uri)
            playbooks.extend(query["results"])

        # Save the most recent timestamp so we only scrape beyond it next time
        if playbooks:
            created_after = cli_utils.increment_timestamp(playbooks[0]["created"])
            self.log.info(f"parsing metrics for {len(playbooks)} playbooks...")

        for playbook in playbooks:
            self.metrics["total"].inc()
            if playbook["duration"] is not None:
                duration = datetime.strptime(playbook["duration"], "%H:%M:%S.%f").time()
                seconds = duration.hour * 3600 + duration.minute * 60 + duration.second + duration.microsecond / 1000000
            else:
                seconds = 0

            self.metrics["playbooks"].labels(
                timestamp=playbook["created"],
                path=playbook["path"],
                status=playbook["status"],
                ansible_version=playbook["ansible_version"],
                python_version=playbook["python_version"],
                client_version=playbook["client_version"],
                server_version=playbook["server_version"],
                plays=playbook["items"]["plays"],
                tasks=playbook["items"]["tasks"],
                results=playbook["items"]["results"],
                hosts=playbook["items"]["hosts"],
                files=playbook["items"]["files"],
                records=playbook["items"]["records"]
            ).observe(seconds)

        self.log.info("finished updating playbook metrics.")
        return (self.metrics, created_after)


class AraTaskCollector(object):
    def __init__(self, client, log, limit):
        self.client = client
        self.log = log
        self.limit = limit

        labels = ["name", "playbook", "status", "path", "action", "duration", "updated", "results"]
        self.metrics = {
            "total": Gauge(f"ara_tasks_total", f"Number of tasks recorded by ara in prometheus"),
            "range": Gauge(f"ara_tasks_range", f"Limit metric collection to the N most recent tasks"),
            "completed": Gauge("ara_tasks_completed", "Completed Ansible tasks", labels),
            "failed": Gauge("ara_tasks_failed", "Failed Ansible tasks", labels),
            "running": Gauge("ara_tasks_running", "Running Ansible tasks", labels),
            "expired": Gauge("ara_tasks_expired", "Expired Ansible tasks", labels)
        }

    def collect_metrics(self, created_after=None):
        self.metrics["range"].set(self.limit)

        query = f"/api/v1/tasks?order=-id&limit={self.limit}"
        if created_after is not None:
            query += f"&created_after={created_after}"

        response = self.client.get(query)
        tasks = response["results"]

        # Iterate through multiple pages of results if necessary
        while response["next"]:
            # For example:
            # "next": "https://demo.recordsansible.org/api/v1/tasks?limit=1000&offset=2000",
            uri = response["next"].replace(self.client.endpoint, "")
            response = self.client.get(uri)
            tasks.extend(response["results"])

        if tasks:
            # Save the most recent timestamp so we only scrape beyond it next time
            created_after = cli_utils.increment_timestamp(tasks[0]["created"])
            self.log.info(f"updating metrics for {len(tasks)} tasks...")

        for task in tasks:
            self.metrics["total"].inc()

            self.metrics[task["status"]].labels(
                name=task["name"],
                playbook=task["playbook"],
                status=task["status"],
                path=task["path"],
                action=task["action"],
                duration=task["duration"],
                updated=task["updated"],
                results=task["items"]["results"],
            ).inc()

        return created_after


class AraHostCollector(object):
    def __init__(self, client, log, limit):
        self.client = client
        self.log = log
        self.limit = limit

        labels = ["name", "playbook", "updated"]
        self.metrics = {
            "total": Gauge(f"ara_hosts_total", f"Hosts recorded by ara"),
            "range": Gauge(f"ara_hosts_range", f"Limit metric collection to the N most recent hosts"),
            "changed": Gauge("ara_hosts_changed", "Number of changes on a host", labels),
            "failed": Gauge("ara_hosts_failed", "Number of failures on a host", labels),
            "ok": Gauge("ara_hosts_ok", "Number of successful tasks without changes on a host", labels),
            "skipped": Gauge("ara_hosts_skipped", "Number of skipped tasks on a host", labels),
            "unreachable": Gauge("ara_hosts_unreachable", "Number of unreachable errors on a host", labels)
        }

    def collect_metrics(self, created_after=None):
        self.metrics["range"].set(self.limit)

        query = f"/api/v1/hosts?order=-id&limit={self.limit}"
        if created_after is not None:
            query += f"&created_after={created_after}"

        response = self.client.get(query)
        hosts = response["results"]

        # Iterate through multiple pages of results if necessary
        while response["next"]:
            # For example:
            # "next": "https://demo.recordsansible.org/api/v1/hosts?limit=1000&offset=2000",
            uri = response["next"].replace(self.client.endpoint, "")
            response = self.client.get(uri)
            hosts.extend(response["results"])

        if hosts:
            # Save the most recent timestamp so we only scrape beyond it next time
            created_after = cli_utils.increment_timestamp(hosts[0]["created"])
            self.log.info(f"updating metrics for {len(hosts)} hosts...")

        for host in hosts:
            self.metrics["total"].inc()
            for status in ["changed", "failed", "ok", "skipped", "unreachable"]:
                if host[status]:
                    self.metrics[status].labels(
                        name=host["name"],
                        playbook=host["playbook"],
                        updated=host["updated"]
                    ).set(host[status])

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

        #playbooks = AraPlaybookCollector(client=client, log=self.log)

        # Host metrics
        hosts = AraHostCollector(client=client, log=self.log, limit=args.host_limit)

        # Task metrics
        tasks = AraTaskCollector(client=client, log=self.log, limit=args.task_limit)

        start_http_server(args.prometheus_port)
        self.log.info(f"ara prometheus exporter listening on http://0.0.0.0:{args.prometheus_port}/metrics")

        created_after = (datetime.now() - timedelta(days=args.max_days)).isoformat()
        self.log.info(f"Backfilling metrics for the last {args.max_days} days since {created_after}... This can take a while based on volume.")
        latest = defaultdict(lambda: created_after)

        while True:
            #playbook_metrics, latest["playbook"] = playbooks.collect_metrics(latest["playbook"], limit=args.playbook_limit)

            latest["hosts"] = hosts.collect_metrics(latest["hosts"])
            latest["tasks"] = tasks.collect_metrics(latest["tasks"])

            time.sleep(args.poll_frequency)
            self.log.info("Checking for updated metrics...")
