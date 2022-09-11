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


class PlayList(Lister):
    """Returns a list of plays based on search queries"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser = global_arguments(parser)
        # fmt: off
        # Play search arguments and ordering as per ara.api.filters.PlayFilter
        parser.add_argument(
            "--playbook",
            metavar="<playbook_id>",
            default=None,
            help=("List plays for the specified playbook"),
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            default=None,
            help=("List plays matching the provided name (full or partial)"),
        )
        parser.add_argument(
            "--uuid",
            metavar="<uuid>",
            default=None,
            help=("List plays matching the provided uuid (full or partial)"),
        )
        parser.add_argument(
            "--status",
            metavar="<status>",
            default=None,
            help=("List plays matching a specific status ('completed', 'running', 'failed')"),
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
            default="-started",
            help=(
                "Orders plays by a field ('id', 'created', 'updated', 'started', 'ended', 'duration')\n"
                "Defaults to '-started' descending so the most recent playbook is at the top.\n"
                "The order can be reversed by omitting the '-': ara play list --order=started"
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

        if args.name is not None:
            query["name"] = args.name

        if args.uuid is not None:
            query["uuid"] = args.uuid

        if args.status is not None:
            query["status"] = args.status

        query["order"] = args.order
        query["limit"] = args.limit

        plays = client.get("/api/v1/plays", **query)
        for play in plays["results"]:
            # Send items to columns
            play["tasks"] = play["items"]["tasks"]
            play["results"] = play["items"]["results"]

            if args.resolve:
                playbook = cli_utils.get_playbook(client, play["playbook"])
                # Paths can easily take up too much width real estate
                if not args.long:
                    play["playbook"] = "(%s) %s" % (playbook["id"], cli_utils.truncatepath(playbook["path"], 50))
                else:
                    play["playbook"] = "(%s) %s" % (playbook["id"], playbook["path"])

        columns = ("id", "status", "name", "playbook", "tasks", "results", "started", "duration")
        # fmt: off
        return (
            columns, (
                [play[column] for column in columns]
                for play in plays["results"]
            )
        )
        # fmt: on


class PlayShow(ShowOne):
    """Returns a detailed view of a specified play"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser = global_arguments(parser)
        # fmt: off
        parser.add_argument(
            "play_id",
            metavar="<play-id>",
            help="Play to show",
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
        play = client.get("/api/v1/plays/%s" % args.play_id)
        if "detail" in play and play["detail"] == "Not found.":
            self.log.error("Play not found: %s" % args.play_id)
            sys.exit(1)

        playbook = "(%s) %s" % (play["playbook"]["id"], play["playbook"]["name"] or play["playbook"]["path"])
        play["report"] = "%s/playbooks/%s.html" % (args.server, play["playbook"]["id"])
        play["playbook"] = playbook

        # fmt: off
        columns = (
            "id",
            "report",
            "status",
            "name",
            "playbook",
            "started",
            "ended",
            "duration",
            "items",
        )
        # fmt: on
        return (columns, ([play[column] for column in columns]))


class PlayDelete(Command):
    """Deletes the specified play and associated resources"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser = global_arguments(parser)
        # fmt: off
        parser.add_argument(
            "play_id",
            metavar="<play-id>",
            help="Play to delete",
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
        client.delete("/api/v1/plays/%s" % args.play_id)
