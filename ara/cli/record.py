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


class RecordList(Lister):
    """Returns a list of records based on search queries"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser = global_arguments(parser)
        # fmt: off
        # Record search arguments and ordering as per ara.api.filters.RecordFilter
        parser.add_argument(
            "--playbook",
            metavar="<playbook_id>",
            default=None,
            help=("List records for the specified playbook"),
        )
        parser.add_argument(
            "--key",
            metavar="<key>",
            default=None,
            help=("List records matching the specified key"),
        )
        parser.add_argument(
            "--long",
            action="store_true",
            default=False,
            help=("Don't truncate paths")
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
            default="-updated",
            help=(
                "Orders records by a field ('id', 'created', 'updated', 'key')\n"
                "Defaults to '-updated' descending so the most recent record is at the top.\n"
                "The order can be reversed by omitting the '-': ara record list --order=updated"
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

        if args.key is not None:
            query["key"] = args.key

        query["order"] = args.order
        query["limit"] = args.limit

        records = client.get("/api/v1/records", **query)
        if args.resolve:
            for record in records["results"]:
                playbook = cli_utils.get_playbook(client, record["playbook"])
                # Paths can easily take up too much width real estate
                if not args.long:
                    record["playbook"] = "(%s) %s" % (playbook["id"], cli_utils.truncatepath(playbook["path"], 50))
                else:
                    record["playbook"] = "(%s) %s" % (playbook["id"], playbook["path"])

        columns = ("id", "key", "type", "playbook", "updated")
        # fmt: off
        return (
            columns, (
                [record[column] for column in columns]
                for record in records["results"]
            )
        )
        # fmt: on


class RecordShow(ShowOne):
    """Returns a detailed view of a specified record"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser = global_arguments(parser)
        # fmt: off
        parser.add_argument(
            "record_id",
            metavar="<record-id>",
            help="Record to show",
        )
        # fmt: on
        return parser

    def take_action(self, args):
        # TODO: Render json properly in pretty tables
        if args.formatter == "table":
            self.log.warn("Rendering using default table formatter, use '-f yaml' or '-f json' for improved display.")

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
        record = client.get("/api/v1/records/%s" % args.record_id)
        if "detail" in record and record["detail"] == "Not found.":
            self.log.error("Record not found: %s" % args.record_id)
            sys.exit(1)

        playbook = "(%s) %s" % (record["playbook"]["id"], record["playbook"]["name"] or record["playbook"]["path"])
        record["report"] = "%s/playbooks/%s.html" % (args.server, record["playbook"]["id"])
        record["playbook"] = playbook

        # fmt: off
        columns = (
            "id",
            "report",
            "playbook",
            "key",
            "value",
            "created",
            "updated",
        )
        # fmt: on
        return (columns, ([record[column] for column in columns]))


class RecordDelete(Command):
    """Deletes the specified record and associated resources"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser = global_arguments(parser)
        # fmt: off
        parser.add_argument(
            "record_id",
            metavar="<record-id>",
            help="Record to delete",
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
        client.delete("/api/v1/records/%s" % args.record_id)
