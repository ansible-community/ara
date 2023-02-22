#!/usr/bin/env python3
import time
from datetime import datetime, timedelta

from prometheus_client import Gauge, start_http_server

from ara.clients.http import AraHttpClient


class AraPlaybookCollector(object):
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.client = AraHttpClient(endpoint=self.endpoint)
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

    def collect_metrics(self, created_after=None, limit=1000):
        log("collecting playbook metrics")
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
            uri = query["next"].replace(self.endpoint, "")
            query = self.client.get(uri)
            playbooks.extend(query["results"])

        # Save the most recent timestamp so we only scrape beyond it next time
        if playbooks:
            created_after = increment_timestamp(playbooks[0]["created"])
            log(f"parsing metrics for {len(playbooks)} playbooks")

        for playbook in playbooks:
            self.metrics["total"].inc()
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

        log("finished updating playbook metrics")
        return (self.metrics, created_after)


class AraTaskCollector(object):
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.client = AraHttpClient(endpoint=self.endpoint)
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
        log("collecting task metrics")
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
            uri = query["next"].replace(self.endpoint, "")
            query = self.client.get(uri)
            tasks.extend(query["results"])

        # Save the most recent timestamp so we only scrape beyond it next time
        if tasks:
            created_after = increment_timestamp(tasks[0]["created"])
            log(f"parsing metrics for {len(tasks)} tasks")

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

        log("finished updating task metrics")
        return (self.metrics, created_after)


class AraHostCollector(object):
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.client = AraHttpClient(endpoint=self.endpoint)
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
        log("collecting host metrics")
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
            uri = query["next"].replace(self.endpoint, "")
            query = self.client.get(uri)
            hosts.extend(query["results"])

        # Save the most recent timestamp so we only scrape beyond it next time
        if hosts:
            created_after = increment_timestamp(hosts[0]["created"])
            log(f"parsing metrics for {len(hosts)} hosts")

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

        log("finished updating host metrics")
        return (self.metrics, created_after)


def increment_timestamp(timestamp, pattern="%Y-%m-%dT%H:%M:%S.%fZ"):
    """
    API timestamps have this python isoformat: 2022-12-08T05:45:38.465607Z
    We want to increment timestamps by one microsecond so we can search for things created after them.
    """
    return (datetime.strptime(timestamp, pattern) + timedelta(microseconds=1)).isoformat()


# TODO: Better logging
def log(msg):
    timestamp = datetime.now().isoformat()
    print(f"{timestamp}: {msg}")


if __name__ == "__main__":
    # Start HTTP server for Prometheus scraping
    start_http_server(8000)
    log("ara Prometheus exporter listening on http://0.0.0.0:8000/metrics")

    # TODO: Add argparse for API client, endpoint, authentication, limit and poll frequency
    playbooks = AraPlaybookCollector(endpoint="https://demo.recordsansible.org")
    tasks = AraTaskCollector(endpoint="https://demo.recordsansible.org")
    hosts = AraHostCollector(endpoint="https://demo.recordsansible.org")

    latest = dict(playbook=None, task=None, host=None)
    while True:
        playbook_metrics, latest["playbook"] = playbooks.collect_metrics(latest["playbook"])
        task_metrics, latest["task"] = tasks.collect_metrics(latest["task"])
        host_metrics, latest["host"] = hosts.collect_metrics(latest["host"])
        time.sleep(30)
