# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
import os
import sys
from datetime import timedelta

from cliff.command import Command
from cliff.lister import Lister
from cliff.show import ShowOne

import ara.cli.utils as cli_utils
from ara.cli.base import global_arguments
from ara.clients.utils import get_client


class TaskList(Lister):
    """Returns a list of tasks based on search queries"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser = global_arguments(parser)
        # fmt: off
        # Task search arguments and ordering as per ara.api.filters.TaskFilter
        parser.add_argument(
            "--playbook",
            metavar="<playbook_id>",
            default=None,
            help=("List tasks for a specified playbook id"),
        )
        parser.add_argument(
            "--status",
            metavar="<status>",
            default=None,
            help=("List tasks matching a specific status ('completed', 'expired', 'failed', 'running' or 'unknown')")
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            default=None,
            help=("List tasks matching the provided name (full or partial)"),
        )
        parser.add_argument(
            "--uuid",
            metavar="<uuid>",
            default=None,
            help=("List tasks matching the provided uuid (full or partial)"),
        )
        parser.add_argument(
            "--path",
            metavar="<path>",
            default=None,
            help=("List tasks matching the provided path (full or partial)"),
        )
        parser.add_argument(
            "--action",
            metavar="<action>",
            default=None,
            help=("List tasks matching a specific action/ansible module (ex: 'debug', 'package', 'set_fact')"),
        )
        parser.add_argument(
            "--long",
            action="store_true",
            default=False,
            help=("Don't truncate paths and include additional fields: path, lineno, handler, play")
        )
        parser.add_argument(
            "--resolve",
            action="store_true",
            default=os.environ.get("ARA_CLI_RESOLVE", False),
            help=("Resolve IDs to identifiers (such as path or names). Defaults to ARA_CLI_RESOLVE or False")
        )
        parser.add_argument(
            "--order",
            metavar="<order>",
            default="-started",
            help=(
                "Orders tasks by a field ('id', 'created', 'updated', 'started', 'ended', 'duration')\n"
                "Defaults to '-started' descending so the most recent task is at the top.\n"
                "The order can be reversed by omitting the '-': ara task list --order=started"
            ),
        )
        parser.add_argument(
            "--limit",
            metavar="<limit>",
            default=os.environ.get("ARA_CLI_LIMIT", 50),
            help=("Returns the first <limit> determined by the ordering. Defaults to ARA_CLI_LIMIT or 50.")
        )
        # fmt: on
        return parser

    def take_action(self, args):
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

        query = {}
        if args.playbook is not None:
            query["playbook"] = args.playbook

        if args.status is not None:
            query["status"] = args.status

        if args.name is not None:
            query["name"] = args.name

        if args.uuid is not None:
            query["uuid"] = args.uuid

        if args.path is not None:
            query["path"] = args.path

        if args.action is not None:
            query["action"] = args.action

        query["order"] = args.order
        query["limit"] = args.limit

        tasks = client.get("/api/v1/tasks", **query)

        for task in tasks["results"]:
            task["results"] = task["items"]["results"]
            if args.resolve:
                playbook = cli_utils.get_playbook(client, task["playbook"])
                # Paths can easily take up too much width real estate
                if not args.long:
                    task["playbook"] = "(%s) %s" % (playbook["id"], cli_utils.truncatepath(playbook["path"], 50))
                else:
                    task["playbook"] = "(%s) %s" % (playbook["id"], playbook["path"])

                if args.long:
                    play = cli_utils.get_play(client, task["play"])
                    task["play"] = "(%s) %s" % (play["id"], play["name"])

        # fmt: off
        if args.long:
            columns = (
                "id",
                "uuid",
                "status",
                "results",
                "action",
                "name",
                "tags",
                "path",
                "lineno",
                "handler",
                "playbook",
                "play",
                "started",
                "duration"
            )
        else:
            columns = (
                "id",
                "status",
                "results",
                "action",
                "name",
                "playbook",
                "started",
                "duration"
            )
        # fmt: off
        return (
            columns, (
                [task[column] for column in columns]
                for task in tasks["results"]
            )
        )
        # fmt: on


class TaskShow(ShowOne):
    """Returns a detailed view of a specified task"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser = global_arguments(parser)
        # fmt: off
        parser.add_argument(
            "task_id",
            metavar="<task-id>",
            help="Task to show",
        )
        # fmt: on
        return parser

    def take_action(self, args):
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

        # TODO: Improve client to be better at handling exceptions
        task = client.get("/api/v1/tasks/%s" % args.task_id)
        if "detail" in task and task["detail"] == "Not found.":
            self.log.error("Task not found: %s" % args.task_id)
            sys.exit(1)

        task["report"] = "%s/playbooks/%s.html" % (args.server, task["playbook"]["id"])
        columns = (
            "id",
            "uuid",
            "report",
            "name",
            "action",
            "status",
            "path",
            "lineno",
            "started",
            "ended",
            "duration",
            "tags",
            "handler",
        )
        return (columns, ([task[column] for column in columns]))


class TaskDelete(Command):
    """Deletes the specified task and associated resources"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser = global_arguments(parser)
        # fmt: off
        parser.add_argument(
            "task_id",
            metavar="<task-id>",
            help="Task to delete",
        )
        # fmt: on
        return parser

    def take_action(self, args):
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

        # TODO: Improve client to be better at handling exceptions
        client.delete("/api/v1/tasks/%s" % args.task_id)


class TaskMetrics(Lister):
    """Provides metrics about actions in tasks"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser = global_arguments(parser)
        # fmt: off
        parser.add_argument(
            "--aggregate",
            choices=["action", "name", "path"],
            default="action",
            help=("Aggregate tasks by action, name or path. Defaults to action."),
        )
        # Task search arguments and ordering as per ara.api.filters.TaskFilter
        parser.add_argument(
            "--playbook",
            metavar="<playbook_id>",
            default=None,
            help=("Filter for tasks for a specified playbook id"),
        )
        parser.add_argument(
            "--status",
            metavar="<status>",
            default=None,
            help=(
                "Filter for tasks matching a specific status "
                "('completed', 'expired', 'failed', 'running', or 'unknown')"
            )
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            default=None,
            help=("Filter for tasks matching the provided name (full or partial)"),
        )
        parser.add_argument(
            "--uuid",
            metavar="<name>",
            default=None,
            help=("Filter for tasks matching the provided uuid (full or partial)"),
        )
        parser.add_argument(
            "--path",
            metavar="<path>",
            default=None,
            help=("Filter for tasks matching the provided path (full or partial)"),
        )
        parser.add_argument(
            "--action",
            metavar="<action>",
            default=None,
            help=("Filter for tasks matching a specific action/ansible module (ex: 'debug', 'package', 'set_fact')"),
        )
        parser.add_argument(
            "--long",
            action="store_true",
            default=False,
            help=(
                "Don't truncate paths and include additional status fields: "
                "completed, expired, failed, running & unknown"
            )
        )
        parser.add_argument(
            "--order",
            metavar="<order>",
            default="-started",
            help=(
                "Orders tasks by a field ('id', 'created', 'updated', 'started', 'ended', 'duration')\n"
                "Defaults to '-started' descending so the most recent task is at the top.\n"
                "The order can be reversed by omitting the '-': ara task metrics --order=started\n"
                "This influences the API request, not the ordering of the metrics."
            ),
        )
        parser.add_argument(
            "--limit",
            metavar="<limit>",
            default=os.environ.get("ARA_CLI_LIMIT", 1000),
            help=("Return metrics for the first <limit> determined by the ordering. Defaults to ARA_CLI_LIMIT or 1000.")
        )
        # fmt: on
        return parser

    def take_action(self, args):
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

        query = {}
        if args.playbook is not None:
            query["playbook"] = args.playbook

        if args.status is not None:
            query["status"] = args.status

        if args.name is not None:
            query["name"] = args.name

        if args.uuid is not None:
            query["uuid"] = args.uuid

        if args.path is not None:
            query["path"] = args.path

        if args.action is not None:
            query["action"] = args.action

        query["order"] = args.order
        query["limit"] = args.limit

        tasks = client.get("/api/v1/tasks", **query)

        # TODO: This could probably be made more efficient without needing to iterate a second time
        # Group tasks by aggregate
        aggregate = {}
        for task in tasks["results"]:
            item = task[args.aggregate]
            if item not in aggregate:
                aggregate[item] = []
            aggregate[item].append(task)

        data = {}
        for item, tasks in aggregate.items():
            data[item] = {
                "count": len(tasks),
                "results": 0,
                "completed": 0,
                "expired": 0,
                "failed": 0,
                "running": 0,
                "unknown": 0,
                "duration_total": 0.0,
            }

            if args.aggregate == "path" and not args.long:
                data[item]["aggregate"] = cli_utils.truncatepath(item, 50)
            else:
                data[item]["aggregate"] = item

            for task in tasks:
                for status in ["completed", "expired", "failed", "running", "unknown"]:
                    if task["status"] == status:
                        data[item][status] += 1

                data[item]["results"] += task["items"]["results"]

                if task["duration"] is not None:
                    data[item]["duration_total"] = cli_utils.sum_timedelta(
                        task["duration"], data[item]["duration_total"]
                    )

            delta = timedelta(seconds=data[item]["duration_total"])
            data[item]["duration_total"] = str(delta)
            data[item]["duration_avg"] = cli_utils.avg_timedelta(delta, data[item]["count"])

        # fmt: off
        if args.long:
            columns = (
                "aggregate",
                "count",
                "results",
                "duration_total",
                "duration_avg",
                "completed",
                "failed",
                "running",
                "expired",
                "unknown",
            )
        else:
            columns = (
                "aggregate",
                "count",
                "results",
                "duration_total",
                "duration_avg",
            )

        return (
            columns, (
                [data[action][column] for column in columns]
                for action in sorted(data.keys())
            )
        )
        # fmt: on
