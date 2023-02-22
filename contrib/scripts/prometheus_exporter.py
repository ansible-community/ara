#!/usr/bin/env python3
import time

from prometheus_client import Gauge, start_http_server

from ara.clients.http import AraHttpClient


class AraPlaybookCollector(object):
    def __init__(self, endpoint, limit=500):
        self.client = AraHttpClient(endpoint=endpoint)
        self.limit = limit
        self.metrics = {
            "total": Gauge("ara_playbooks_total", "Total number of playbooks recorded by ara"),
            "range": Gauge("ara_playbooks_range", "Limit metric collection to the N most recent playbooks"),
            "playbooks": Gauge(
                "ara_playbooks",
                "Ansible playbooks recorded by ara",
                [
                    "path",
                    "status",
                    "ansible_version",
                    "python_version",
                    "client_version",
                    "server_version",
                    "plays",
                    "tasks",
                    "results",
                    "hosts",
                    "files",
                    "records",
                ],
            ),
        }

    def collect_metrics(self):
        # TODO: Reset gauges until we figure out how to not increment every time it runs
        for metric in self.metrics:
            try:
                self.metrics[metric]._metrics.clear()
            except AttributeError:
                pass

        playbooks = self.client.get(f"/api/v1/playbooks?limit={self.limit}")
        self.metrics["total"].set(playbooks["count"])
        self.metrics["range"].set(self.limit)

        for playbook in playbooks["results"]:
            self.metrics["playbooks"].labels(
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
                records=playbook["items"]["records"],
            ).inc()

        return self.metrics


class AraTaskCollector(object):
    def __init__(self, endpoint, limit=500):
        self.client = AraHttpClient(endpoint=endpoint)
        self.limit = limit
        self.metrics = {
            "total": Gauge("ara_tasks_total", "Total number of tasks recorded by ara"),
            "range": Gauge("ara_tasks_range", "Limit metric collection to the N most recent tasks"),
            "tasks": Gauge(
                "ara_tasks",
                "Ansible tasks recorded by ara",
                ["path", "lineno", "status", "name", "action", "results"],
            ),
        }

    def collect_metrics(self):
        # TODO: Reset gauges until we figure out how to not increment every time it runs
        for metric in self.metrics:
            try:
                self.metrics[metric]._metrics.clear()
            except AttributeError:
                pass

        tasks = self.client.get(f"/api/v1/tasks?limit={self.limit}")
        self.metrics["total"].set(tasks["count"])
        self.metrics["range"].set(self.limit)

        for task in tasks["results"]:
            self.metrics["tasks"].labels(
                path=task["path"],
                lineno=task["lineno"],
                status=task["status"],
                name=task["name"],
                action=task["action"],
                results=task["items"]["results"],
            ).inc()

        return self.metrics


class AraHostCollector(object):
    def __init__(self, endpoint, limit=500):
        self.client = AraHttpClient(endpoint=endpoint)
        self.limit = limit
        self.metrics = {
            "total": Gauge("ara_hosts_total", "Total number of hosts recorded by ara"),
            "range": Gauge("ara_hosts_range", "Limit metric collection to the N most recent hosts"),
            "hosts": Gauge(
                "ara_hosts",
                "Ansible hosts recorded by ara",
                ["name", "changed", "failed", "ok", "skipped", "unreachable"],
            ),
        }

    def collect_metrics(self):
        # TODO: Reset gauges until we figure out how to not increment every time it runs
        for metric in self.metrics:
            try:
                self.metrics[metric]._metrics.clear()
            except AttributeError:
                pass

        hosts = self.client.get(f"/api/v1/hosts?limit={self.limit}")
        self.metrics["total"].set(hosts["count"])
        self.metrics["range"].set(self.limit)

        for host in hosts["results"]:
            self.metrics["hosts"].labels(
                name=host["name"],
                changed=host["changed"],
                failed=host["failed"],
                ok=host["ok"],
                skipped=host["skipped"],
                unreachable=host["unreachable"],
            ).inc()

        return self.metrics


if __name__ == "__main__":
    # Start HTTP server for Prometheus scraping
    start_http_server(8000)
    # TODO: Add argparse for API client, endpoint, authentication, limit and poll frequency
    playbooks = AraPlaybookCollector(endpoint="https://demo.recordsansible.org")
    tasks = AraTaskCollector(endpoint="https://demo.recordsansible.org")
    hosts = AraHostCollector(endpoint="https://demo.recordsansible.org")

    while True:
        playbooks.collect_metrics()
        tasks.collect_metrics()
        hosts.collect_metrics()
        time.sleep(60)
