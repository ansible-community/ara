# Copyright (c) 2020 The ARA Records Ansible authors
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


class HostList(Lister):
    """ Returns a list of hosts based on search queries """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(HostList, self).get_parser(prog_name)
        parser = global_arguments(parser)
        # fmt: off
        # Host search arguments and ordering as per ara.api.filters.HostFilter
        # TODO: non-exhaustive (searching for failed, ok, unreachable, etc.)
        parser.add_argument(
            "--name",
            metavar="<name>",
            default=None,
            help=("List hosts matching the provided name (full or partial)"),
        )
        parser.add_argument(
            "--playbook",
            metavar="<playbook_id>",
            default=None,
            help=("List hosts for a specified playbook id"),
        )

        changed = parser.add_mutually_exclusive_group()
        changed.add_argument(
            "--with-changed",
            action="store_true",
            default=False,
            help=("Return hosts with changed results")
        )
        changed.add_argument(
            "--without-changed",
            action="store_true",
            default=False,
            help=("Don't return hosts with changed results")
        )

        failed = parser.add_mutually_exclusive_group()
        failed.add_argument(
            "--with-failed",
            action="store_true",
            default=False,
            help=("Return hosts with failed results")
        )
        failed.add_argument(
            "--without-failed",
            action="store_true",
            default=False,
            help=("Don't return hosts with failed results")
        )

        unreachable = parser.add_mutually_exclusive_group()
        unreachable.add_argument(
            "--with-unreachable",
            action="store_true",
            default=False,
            help=("Return hosts with unreachable results")
        )
        unreachable.add_argument(
            "--without-unreachable",
            action="store_true",
            default=False,
            help=("Don't return hosts with unreachable results")
        )
        parser.add_argument(
            "--resolve",
            action="store_true",
            default=os.environ.get("ARA_CLI_RESOLVE", False),
            help=("Resolve IDs to identifiers (such as path or names). Defaults to ARA_CLI_RESOLVE or False")
        )
        parser.add_argument(
            "--long",
            action="store_true",
            default=False,
            help=("Don't truncate paths")
        )
        parser.add_argument(
            "--order",
            metavar="<order>",
            default="-updated",
            help=(
                "Orders hosts by a field ('id', 'created', 'updated', 'name')\n"
                "Defaults to '-updated' descending so the most recent host is at the top.\n"
                "The order can be reversed by omitting the '-': ara host list --order=updated"
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
        if args.name is not None:
            query["name"] = args.name

        if args.playbook is not None:
            query["playbook"] = args.playbook

        if args.with_changed:
            query["changed__gt"] = 0
        if args.without_changed:
            query["changed__lt"] = 1
        if args.with_failed:
            query["failed__gt"] = 0
        if args.without_failed:
            query["failed__lt"] = 1
        if args.with_unreachable:
            query["unreachable__gt"] = 0
        if args.without_unreachable:
            query["unreachable__lt"] = 1

        query["order"] = args.order
        query["limit"] = args.limit

        hosts = client.get("/api/v1/hosts", **query)

        if args.resolve:
            for host in hosts["results"]:
                playbook = cli_utils.get_playbook(client, host["playbook"])
                # Paths can easily take up too much width real estate
                if not args.long:
                    host["playbook"] = "(%s) %s" % (playbook["id"], cli_utils.truncatepath(playbook["path"], 50))
                else:
                    host["playbook"] = "(%s) %s" % (playbook["id"], playbook["path"])

        columns = ("id", "name", "playbook", "changed", "failed", "ok", "skipped", "unreachable", "updated")
        # fmt: off
        return (
            columns, (
                [host[column] for column in columns]
                for host in hosts["results"]
            )
        )
        # fmt: on


class HostShow(ShowOne):
    """ Returns a detailed view of a specified host """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(HostShow, self).get_parser(prog_name)
        parser = global_arguments(parser)
        # fmt: off
        parser.add_argument(
            "host_id",
            metavar="<host-id>",
            help="Host to show",
        )
        parser.add_argument(
            "--with-facts",
            action="store_true",
            help="Also include host facts in the response (use with '-f json' or '-f yaml')"
        )
        # fmt: on
        return parser

    def take_action(self, args):
        # TODO: Render json properly in pretty tables
        if args.with_facts and args.formatter == "table":
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
        host = client.get("/api/v1/hosts/%s" % args.host_id)
        if "detail" in host and host["detail"] == "Not found.":
            self.log.error("Host not found: %s" % args.host_id)
            sys.exit(1)

        host["report"] = "%s/playbooks/%s.html" % (args.server, host["playbook"]["id"])
        if args.with_facts:
            # fmt: off
            columns = (
                "id",
                "report",
                "name",
                "changed",
                "failed",
                "ok",
                "skipped",
                "unreachable",
                "facts",
                "updated"
            )
            # fmt: on
        else:
            # fmt: off
            columns = (
                "id",
                "report",
                "name",
                "changed",
                "failed",
                "ok",
                "skipped",
                "unreachable",
                "updated"
            )
            # fmt: on
        return (columns, ([host[column] for column in columns]))


class HostDelete(Command):
    """ Deletes the specified host and associated resources """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(HostDelete, self).get_parser(prog_name)
        parser = global_arguments(parser)
        # fmt: off
        parser.add_argument(
            "host_id",
            metavar="<host-id>",
            help="Host to delete",
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
        client.delete("/api/v1/hosts/%s" % args.host_id)
