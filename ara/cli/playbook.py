# Copyright (c) 2020 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
import os
import sys
from datetime import datetime, timedelta

from cliff.command import Command
from cliff.lister import Lister
from cliff.show import ShowOne

import ara.cli.utils as cli_utils
from ara.cli.base import global_arguments
from ara.clients.utils import get_client


class PlaybookList(Lister):
    """ Returns a list of playbooks based on search queries """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(PlaybookList, self).get_parser(prog_name)
        parser = global_arguments(parser)
        # fmt: off
        # Playbook search arguments and ordering as per ara.api.filters.PlaybookFilter
        parser.add_argument(
            "--label",
            metavar="<label>",
            default=None,
            help=("List playbooks matching the provided label"),
        )
        parser.add_argument(
            "--controller",
            metavar="<controller>",
            default=None,
            help=("List playbooks that ran from the provided controller (full or partial)"),
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            default=None,
            help=("List playbooks matching the provided name (full or partial)"),
        )
        parser.add_argument(
            "--path",
            metavar="<path>",
            default=None,
            help=("List playbooks matching the provided path (full or partial)"),
        )
        parser.add_argument(
            "--status",
            metavar="<status>",
            default=None,
            help=("List playbooks matching a specific status ('completed', 'running', 'failed')"),
        )
        parser.add_argument(
            "--long",
            action="store_true",
            default=False,
            help=("Don't truncate paths and include additional fields: name, plays, files, records")
        )
        parser.add_argument(
            "--order",
            metavar="<order>",
            default="-started",
            help=(
                "Orders playbooks by a field ('id', 'created', 'updated', 'started', 'ended', 'duration')\n"
                "Defaults to '-started' descending so the most recent playbook is at the top.\n"
                "The order can be reversed by omitting the '-': ara playbook list --order=started"
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
        client = get_client(
            client=args.client,
            endpoint=args.server,
            timeout=args.timeout,
            username=args.username,
            password=args.password,
            verify=False if args.insecure else True,
            run_sql_migrations=False,
        )
        query = {}
        if args.label is not None:
            query["label"] = args.label

        if args.controller is not None:
            query["controller"] = args.controller

        if args.name is not None:
            query["name"] = args.name

        if args.path is not None:
            query["path"] = args.path

        if args.status is not None:
            query["status"] = args.status

        query["order"] = args.order
        query["limit"] = args.limit

        playbooks = client.get("/api/v1/playbooks", **query)
        for playbook in playbooks["results"]:
            # Send items to columns
            playbook["plays"] = playbook["items"]["plays"]
            playbook["tasks"] = playbook["items"]["tasks"]
            playbook["results"] = playbook["items"]["results"]
            playbook["hosts"] = playbook["items"]["hosts"]
            playbook["files"] = playbook["items"]["files"]
            playbook["records"] = playbook["items"]["records"]
            # Paths can easily take up too much width real estate
            if not args.long:
                playbook["path"] = cli_utils.truncatepath(playbook["path"], 50)

        # fmt: off
        if args.long:
            columns = (
                "id",
                "status",
                "controller",
                "name",
                "path",
                "plays",
                "tasks",
                "results",
                "hosts",
                "files",
                "records",
                "started",
                "duration"
            )
        else:
            columns = (
                "id",
                "status",
                "controller",
                "path",
                "tasks",
                "results",
                "hosts",
                "started",
                "duration"
            )
        return (
            columns, (
                [playbook[column] for column in columns]
                for playbook in playbooks["results"]
            )
        )
        # fmt: on


class PlaybookShow(ShowOne):
    """ Returns a detailed view of a specified playbook """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(PlaybookShow, self).get_parser(prog_name)
        parser = global_arguments(parser)
        # fmt: off
        parser.add_argument(
            "playbook_id",
            metavar="<playbook-id>",
            help="Playbook to show",
        )
        # fmt: on
        return parser

    def take_action(self, args):
        # TODO: Render json properly in pretty tables
        if args.formatter == "table":
            self.log.warn("Rendering using default table formatter, use '-f yaml' or '-f json' for improved display.")

        client = get_client(
            client=args.client,
            endpoint=args.server,
            timeout=args.timeout,
            username=args.username,
            password=args.password,
            verify=False if args.insecure else True,
            run_sql_migrations=False,
        )

        # TODO: Improve client to be better at handling exceptions
        playbook = client.get("/api/v1/playbooks/%s" % args.playbook_id)
        if "detail" in playbook and playbook["detail"] == "Not found.":
            self.log.error("Playbook not found: %s" % args.playbook_id)
            sys.exit(1)

        playbook["report"] = "%s/playbooks/%s.html" % (args.server, args.playbook_id)
        columns = (
            "id",
            "report",
            "controller",
            "status",
            "path",
            "started",
            "ended",
            "duration",
            "ansible_version",
            "items",
            "labels",
            "arguments",
        )
        return (columns, ([playbook[column] for column in columns]))


class PlaybookDelete(Command):
    """ Deletes the specified playbook and associated resources """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(PlaybookDelete, self).get_parser(prog_name)
        parser = global_arguments(parser)
        # fmt: off
        parser.add_argument(
            "playbook_id",
            metavar="<playbook-id>",
            help="Playbook to delete",
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
            run_sql_migrations=False,
        )

        # TODO: Improve client to be better at handling exceptions
        client.delete("/api/v1/playbooks/%s" % args.playbook_id)


class PlaybookPrune(Command):
    """ Deletes playbooks beyond a specified age in days """

    log = logging.getLogger(__name__)
    deleted = 0

    def get_parser(self, prog_name):
        parser = super(PlaybookPrune, self).get_parser(prog_name)
        parser = global_arguments(parser)
        # fmt: off
        parser.add_argument(
            "--days", type=int, default=31, help="Delete playbooks started this many days ago (default: 31)"
        )
        # Playbook search arguments like 'ara playbook list'
        parser.add_argument(
            "--label",
            metavar="<label>",
            default=None,
            help=("Only delete playbooks matching the provided label"),
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            default=None,
            help=("Only delete playbooks matching the provided name (full or partial)"),
        )
        parser.add_argument(
            "--controller",
            metavar="<controller>",
            default=None,
            help=("Only delete playbooks that ran from the provided controller (full or partial)"),
        )
        parser.add_argument(
            "--path",
            metavar="<path>",
            default=None,
            help=("Only delete only playbooks matching the provided path (full or partial)"),
        )
        parser.add_argument(
            "--status",
            metavar="<status>",
            default=None,
            help=("Only delete playbooks matching a specific status ('completed', 'running', 'failed')"),
        )
        parser.add_argument(
            "--order",
            metavar="<order>",
            default="started",
            help=(
                "Orders playbooks by a field ('id', 'created', 'updated', 'started', 'ended', 'duration')\n"
                "Defaults to 'started' descending so the oldest playbook would be deleted first.\n"
                "The order can be reversed by using '-': ara playbook list --order=-started"
            ),
        )
        parser.add_argument(
            "--limit",
            metavar="<limit>",
            default=os.environ.get("ARA_CLI_LIMIT", 200),
            help=("Only delete the first <limit> determined by the ordering. Defaults to ARA_CLI_LIMIT or 200.")
        )
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Confirm deletion of playbooks, otherwise runs without deleting any playbook",
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
            run_sql_migrations=False,
        )

        if not args.confirm:
            self.log.info("--confirm was not specified, no playbooks will be deleted")

        query = {}
        if args.label is not None:
            query["label"] = args.label

        if args.controller is not None:
            query["controller"] = args.controller

        if args.name is not None:
            query["name"] = args.name

        if args.path is not None:
            query["path"] = args.path

        if args.status is not None:
            query["status"] = args.status

        # generate a timestamp from n days ago in a format we can query the API with
        # ex: 2019-11-21T00:57:41.702229
        query["started_before"] = (datetime.now() - timedelta(days=args.days)).isoformat()
        query["order"] = args.order
        query["limit"] = args.limit

        playbooks = client.get("/api/v1/playbooks", **query)

        # TODO: Improve client validation and exception handling
        if "count" not in playbooks:
            # If we didn't get an answer we can parse, it's probably due to an error 500, 403, 401, etc.
            # The client would have logged the error.
            self.log.error("Client failed to retrieve results, see logs for ara.clients.offline or ara.clients.http.")
            sys.exit(1)

        self.log.info("Found %s playbooks matching query" % playbooks["count"])
        for playbook in playbooks["results"]:
            if not args.confirm:
                msg = "Dry-run: playbook {id} ({path}) would have been deleted, start date: {started}"
                self.log.info(msg.format(id=playbook["id"], path=playbook["path"], started=playbook["started"]))
            else:
                msg = "Deleting playbook {id} ({path}), start date: {started}"
                self.log.info(msg.format(id=playbook["id"], path=playbook["path"], started=playbook["started"]))
                client.delete("/api/v1/playbooks/%s" % playbook["id"])
                self.deleted += 1

        self.log.info("%s playbooks deleted" % self.deleted)


class PlaybookMetrics(Lister):
    """ Provides metrics about playbooks """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(PlaybookMetrics, self).get_parser(prog_name)
        parser = global_arguments(parser)
        # fmt: off
        parser.add_argument(
            "--aggregate",
            choices=["name", "path", "ansible_version", "controller"],
            default="path",
            help=("Aggregate playbooks by path, name, ansible version or controller. Defaults to path."),
        )
        # Playbook search arguments and ordering as per ara.api.filters.PlaybookFilter
        parser.add_argument(
            "--label",
            metavar="<label>",
            default=None,
            help=("List playbooks matching the provided label"),
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            default=None,
            help=("List playbooks matching the provided name (full or partial)"),
        )
        parser.add_argument(
            "--path",
            metavar="<path>",
            default=None,
            help=("List playbooks matching the provided path (full or partial)"),
        )
        parser.add_argument(
            "--status",
            metavar="<status>",
            default=None,
            help=("List playbooks matching a specific status ('completed', 'running', 'failed')"),
        )
        parser.add_argument(
            "--long",
            action="store_true",
            default=False,
            help=("Don't truncate paths and include additional fields: name, plays, files, records")
        )
        parser.add_argument(
            "--order",
            metavar="<order>",
            default="-started",
            help=(
                "Orders playbooks by a field ('id', 'created', 'updated', 'started', 'ended', 'duration')\n"
                "Defaults to '-started' descending so the most recent playbook is at the top.\n"
                "The order can be reversed by omitting the '-': ara playbook list --order=started"
            ),
        )
        parser.add_argument(
            "--limit",
            metavar="<limit>",
            default=os.environ.get("ARA_CLI_LIMIT", 1000),
            help=("Returns the first <limit> determined by the ordering. Defaults to ARA_CLI_LIMIT or 1000.")
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
            run_sql_migrations=False,
        )
        query = {}
        if args.label is not None:
            query["label"] = args.label

        if args.name is not None:
            query["name"] = args.name

        if args.path is not None:
            query["path"] = args.path

        if args.status is not None:
            query["status"] = args.status

        query["order"] = args.order
        query["limit"] = args.limit

        playbooks = client.get("/api/v1/playbooks", **query)

        # TODO: This could probably be made more efficient without needing to iterate a second time
        # Group playbooks by aggregate
        aggregate = {}
        for playbook in playbooks["results"]:
            item = playbook[args.aggregate]
            if item not in aggregate:
                aggregate[item] = []
            aggregate[item].append(playbook)

        data = {}
        for item, playbooks in aggregate.items():
            data[item] = {
                "count": len(playbooks),
                "hosts": 0,
                "plays": 0,
                "tasks": 0,
                "results": 0,
                "files": 0,
                "records": 0,
                "expired": 0,
                "failed": 0,
                "running": 0,
                "completed": 0,
                "unknown": 0,
                "duration_total": "00:00:00.000000",
            }

            if args.aggregate == "path" and not args.long:
                data[item]["aggregate"] = cli_utils.truncatepath(item, 50)
            else:
                data[item]["aggregate"] = item

            for playbook in playbooks:
                for status in ["completed", "expired", "failed", "running", "unknown"]:
                    if playbook["status"] == status:
                        data[item][status] += 1

                for obj in ["files", "hosts", "plays", "tasks", "records", "results"]:
                    data[item][obj] += playbook["items"][obj]

                if playbook["duration"] is not None:
                    data[item]["duration_total"] = cli_utils.sum_timedelta(
                        playbook["duration"], data[item]["duration_total"]
                    )

            data[item]["duration_avg"] = cli_utils.avg_timedelta(data[item]["duration_total"], data[item]["count"])

        # fmt: off
        if args.long:
            columns = (
                "aggregate",
                "count",
                "duration_total",
                "duration_avg",
                "plays",
                "tasks",
                "results",
                "hosts",
                "files",
                "records",
                "completed",
                "expired",
                "failed",
                "running",
                "unknown"
            )
        else:
            columns = (
                "aggregate",
                "count",
                "duration_total",
                "duration_avg",
                "tasks",
                "results",
                "hosts",
                "completed",
                "failed",
                "running"
            )
        return (
            columns, (
                [data[playbook][column] for column in columns]
                for playbook in sorted(data.keys())
            )
        )
        # fmt: on
