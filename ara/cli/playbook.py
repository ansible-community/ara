# Copyright (c) 2020 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging

from cliff.lister import Lister

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
            "--order",
            metavar="<order>",
            default="-started",
            help=(
                "Orders results by a field ('id', 'created', 'updated', 'started', 'ended', 'duration')\n"
                "Defaults to '-started' descending so the most recent playbook is at the top.\n"
                "The order can be reversed by omitting the '-': ara playbook list --order=started"
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
        columns = ("id", "status", "path", "started", "duration")
        # fmt: off
        return (
            columns, (
                [playbook[column] for column in columns]
                for playbook in playbooks["results"]
            )
        )
        # fmt: on
