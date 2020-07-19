# Copyright (c) 2020 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging

from cliff.lister import Lister

from ara.cli.base import global_arguments
from ara.clients.utils import get_client


class TaskList(Lister):
    """ Returns a list of tasks based on search queries """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(TaskList, self).get_parser(prog_name)
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
            help=("List tasks matching a specific status ('completed', 'running' or 'unknown')")
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            default=None,
            help=("List tasks matching the provided name (full or partial)"),
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
            default=100,
            help=("Returns the first <limit> determined by the ordering. Defaults to 100.")
        )
        # fmt: on
        return parser

    def take_action(self, args):
        client = get_client(
            client=args.client,
            endpoint=args.server,
            timeout=args.timeout,
            username=args.username,
            password=args.password,
            verify=False if args.insecure else True,
        )
        query = {}
        if args.playbook is not None:
            query["playbook"] = args.playbook

        if args.status is not None:
            query["status"] = args.status

        if args.name is not None:
            query["name"] = args.name

        if args.path is not None:
            query["path"] = args.path

        if args.action is not None:
            query["action"] = args.action

        query["order"] = args.order
        query["limit"] = args.limit

        tasks = client.get("/api/v1/tasks", **query)
        columns = ("id", "playbook", "status", "action", "name", "started", "duration")
        # fmt: off
        return (
            columns, (
                [task[column] for column in columns]
                for task in tasks["results"]
            )
        )
        # fmt: on
