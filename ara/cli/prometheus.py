# Copyright (c) 2023 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
import os
import sys
import time
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
    def __init__(self, client, log):
        self.client = client
        self.log = log
        self.metrics = {
            "total": Gauge("ara_tasks_total", "Total number of tasks recorded by ara"),
            "range": Gauge("ara_tasks_range", "Limit metric collection to the N most recent tasks"),
            "tasks": Gauge(
                "ara_tasks",
                "Ansible tasks recorded by ara",
                ["path", "lineno", "status", "name", "action", "results"],
            ),
        }

    def collect_metrics(self, created_after=None, limit=2500):
        self.log.info("collecting task metrics...")
        self.metrics["range"].set(limit)

        if created_after is None:
            query = self.client.get(f"/api/v1/tasks?order=-id&limit={limit}")
        else:
            query = self.client.get(f"/api/v1/tasks?order=-id&limit={limit}&created_after={created_after}")
        tasks = query["results"]

        # Iterate through multiple pages of results if necessary
        while query["next"]:
            # For example:
            # "next": "https://demo.recordsansible.org/api/v1/tasks?limit=1000&offset=2000",
            uri = query["next"].replace(self.client.endpoint, "")
            query = self.client.get(uri)
            tasks.extend(query["results"])

        # Save the most recent timestamp so we only scrape beyond it next time
        if tasks:
            created_after = cli_utils.increment_timestamp(tasks[0]["created"])
            self.log.info(f"parsing metrics for {len(tasks)} tasks...")

        for task in tasks:
            self.metrics["total"].inc()
            self.metrics["tasks"].labels(
                path=task["path"],
                lineno=task["lineno"],
                status=task["status"],
                name=task["name"],
                action=task["action"],
                results=task["items"]["results"],
            ).inc()

        self.log.info("finished updating task metrics.")
        return (self.metrics, created_after)


class AraHostCollector(object):
    def __init__(self, client, log):
        self.client = client
        self.log = log
        self.metrics = {
            "total": Gauge("ara_hosts_total", "Total number of hosts recorded by ara"),
            "range": Gauge("ara_hosts_range", "Limit metric collection to the N most recent hosts"),
            "hosts": Gauge(
                "ara_hosts",
                "Ansible hosts recorded by ara",
                ["name", "changed", "failed", "ok", "skipped", "unreachable"],
            ),
        }

    def collect_metrics(self, created_after=None, limit=2500):
        self.log.info("collecting host metrics...")
        self.metrics["range"].set(limit)

        if created_after is None:
            query = self.client.get(f"/api/v1/hosts?order=-id&limit={limit}")
        else:
            query = self.client.get(f"/api/v1/hosts?order=-id&limit={limit}&created_after={created_after}")
        hosts = query["results"]

        # Iterate through multiple pages of results if necessary
        while query["next"]:
            # For example:
            # "next": "https://demo.recordsansible.org/api/v1/hosts?limit=1000&offset=2000",
            uri = query["next"].replace(self.client.endpoint, "")
            query = self.client.get(uri)
            hosts.extend(query["results"])

        # Save the most recent timestamp so we only scrape beyond it next time
        if hosts:
            created_after = cli_utils.increment_timestamp(hosts[0]["created"])
            self.log.info(f"parsing metrics for {len(hosts)} hosts...")

        for host in hosts:
            self.metrics["total"].inc()
            self.metrics["hosts"].labels(
                name=host["name"],
                changed=host["changed"],
                failed=host["failed"],
                ok=host["ok"],
                skipped=host["skipped"],
                unreachable=host["unreachable"],
            ).inc()

        self.log.info("finished updating host metrics.")
        return (self.metrics, created_after)


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

        playbooks = AraPlaybookCollector(client=client, log=self.log)
        tasks = AraTaskCollector(client=client, log=self.log)
        hosts = AraHostCollector(client=client, log=self.log)

        start_http_server(args.prometheus_port)
        self.log.info(f"ara prometheus exporter listening on http://0.0.0.0:{args.prometheus_port}/metrics")

        created_after = (datetime.now() - timedelta(days=args.max_days)).isoformat()
        self.log.info(f"backfilling metrics for the last {args.max_days} days since {created_after}...")
        latest = dict(
            playbook=created_after,
            task=created_after,
            host=created_after
        )
        while True:
            playbook_metrics, latest["playbook"] = playbooks.collect_metrics(latest["playbook"], limit=args.playbook_limit)
            host_metrics, latest["host"] = hosts.collect_metrics(latest["host"], limit=args.host_limit)
            task_metrics, latest["task"] = tasks.collect_metrics(latest["task"], limit=args.task_limit)
            time.sleep(args.poll_frequency)
