# Copyright (c) 2020 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
import sys

from cliff.lister import Lister
from cliff.show import ShowOne

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
        parser.add_argument(
            "--order",
            metavar="<order>",
            default="-updated",
            help=(
                "Orders results by a field ('id', 'created', 'updated', 'name')\n"
                "Defaults to '-updated' descending so the most recent host is at the top.\n"
                "The order can be reversed by omitting the '-': ara host list --order=updated"
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
        if args.name is not None:
            query["name"] = args.name

        if args.playbook is not None:
            query["playbook"] = args.playbook

        query["order"] = args.order
        query["limit"] = args.limit

        hosts = client.get("/api/v1/hosts", **query)
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
