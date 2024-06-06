# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
import os
import sys

from cliff.command import Command
from cliff.lister import Lister
from cliff.show import ShowOne

import ara.cli.utils as cli_utils
from ara.cli.base import global_arguments
from ara.clients.utils import get_client


class ResultList(Lister):
    """Returns a list of results based on search queries"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser = global_arguments(parser)
        # fmt: off
        # Result search arguments and ordering as per ara.api.filters.ResultFilter
        # TODO: non-exhaustive (searching for failed, ok, unreachable, etc.)
        parser.add_argument(
            "--playbook",
            metavar="<playbook_id>",
            default=None,
            help=("List results for the specified playbook"),
        )
        parser.add_argument(
            "--play",
            metavar="<play_id>",
            default=None,
            help=("List results for the specified play"),
        )
        parser.add_argument(
            "--task",
            metavar="<task_id>",
            default=None,
            help=("List results for the specified task"),
        )
        parser.add_argument(
            "--host",
            metavar="<host_id>",
            default=None,
            help=("List results for the specified host"),
        )
        parser.add_argument(
            "--status",
            metavar="<status>",
            default=None,
            help=(
                "List results matching a specific status:\n"
                "ok, failed, skipped, unreachable, changed, ignored, unknown"
            )
        )
        parser.add_argument(
            "--ignore-errors",
            action="store_true",
            default=False,
            help=("Return only results with 'ignore_errors: true', defaults to false")
        )
        parser.add_argument(
            "--changed",
            action="store_true",
            default=False,
            help=("Return only changed results, defaults to false")
        )
        parser.add_argument(
            "--long",
            action="store_true",
            default=False,
            help=("Don't truncate paths and include additional fields: changed, ignore_errors, play")
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
                "Orders results by a field ('id', 'started', 'updated', 'ended', 'duration')\n"
                "Defaults to '-started' descending so the most recent result is at the top.\n"
                "The order can be reversed by omitting the '-': ara result list --order=started"
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
        if args.play is not None:
            query["play"] = args.play
        if args.task is not None:
            query["task"] = args.task
        if args.host is not None:
            query["host"] = args.host

        if args.status is not None:
            query["status"] = args.status

        if args.changed:
            query["changed"] = args.changed

        query["ignore_errors"] = args.ignore_errors
        query["order"] = args.order
        query["limit"] = args.limit

        results = client.get("/api/v1/results", **query)

        if args.resolve:
            for result in results["results"]:
                playbook = cli_utils.get_playbook(client, result["playbook"])
                # Paths can easily take up too much width real estate
                if not args.long:
                    result["playbook"] = "(%s) %s" % (playbook["id"], cli_utils.truncatepath(playbook["path"], 50))
                else:
                    result["playbook"] = "(%s) %s" % (playbook["id"], playbook["path"])

                task = cli_utils.get_task(client, result["task"])
                result["task"] = "(%s) %s" % (task["id"], task["name"])

                host = cli_utils.get_host(client, result["host"])
                result["host"] = "(%s) %s" % (host["id"], host["name"])

                if args.long:
                    play = cli_utils.get_play(client, result["play"])
                    result["play"] = "(%s) %s" % (play["id"], play["name"])

        # fmt: off
        if args.long:
            columns = (
                "id",
                "status",
                "changed",
                "ignore_errors",
                "playbook",
                "play",
                "task",
                "host",
                "started",
                "duration",
            )
        else:
            columns = (
                "id",
                "status",
                "playbook",
                "task",
                "host",
                "started",
                "duration",
            )

        return (
            columns, (
                [result[column] for column in columns]
                for result in results["results"]
            )
        )
        # fmt: on


class ResultShow(ShowOne):
    """Returns a detailed view of a specified result"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser = global_arguments(parser)
        # fmt: off
        parser.add_argument(
            "result_id",
            metavar="<result-id>",
            help="Result to show",
        )
        parser.add_argument(
            "--with-content",
            action="store_true",
            help="Also include the result content in the response (use with '-f json' or '-f yaml')"
        )
        # fmt: on
        return parser

    def take_action(self, args):
        # TODO: Render json properly in pretty tables
        if args.with_content and args.formatter == "table":
            self.log.warning(
                "Rendering using default table formatter, use '-f yaml' or '-f json' for improved display."
            )

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
        result = client.get("/api/v1/results/%s" % args.result_id)
        if "detail" in result and result["detail"] == "Not found.":
            self.log.error("Result not found: %s" % args.result_id)
            sys.exit(1)

        # Parse data from playbook and format it for display
        result["ansible_version"] = result["playbook"]["ansible_version"]
        playbook = "(%s) %s" % (result["playbook"]["id"], result["playbook"]["name"] or result["playbook"]["path"])
        result["report"] = "%s/playbooks/%s.html" % (args.server, result["playbook"]["id"])
        result["playbook"] = playbook

        # Parse data from play and format it for display
        play = "(%s) %s" % (result["play"]["id"], result["play"]["name"])
        result["play"] = play

        # Parse data from task and format it for display
        task = "(%s) %s" % (result["task"]["id"], result["task"]["name"])
        path = "(%s) %s:%s" % (result["task"]["file"], result["task"]["path"], result["task"]["lineno"])
        result["task"] = task
        result["path"] = path

        if args.with_content:
            columns = (
                "id",
                "report",
                "status",
                "playbook",
                "play",
                "task",
                "path",
                "started",
                "ended",
                "duration",
                "ansible_version",
                "content",
            )
        else:
            columns = (
                "id",
                "report",
                "status",
                "playbook",
                "play",
                "task",
                "path",
                "started",
                "ended",
                "duration",
                "ansible_version",
            )
        return (columns, ([result[column] for column in columns]))


class ResultDelete(Command):
    """Deletes the specified result and associated resources"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser = global_arguments(parser)
        # fmt: off
        parser.add_argument(
            "result_id",
            metavar="<result-id>",
            help="Result to delete",
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
        client.delete("/api/v1/results/%s" % args.result_id)
