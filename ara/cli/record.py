# Copyright (c) 2020 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
import os

from cliff.lister import Lister

from ara.cli.base import global_arguments
from ara.clients.utils import get_client


class RecordList(Lister):
    """ Returns a list of records based on search queries """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(RecordList, self).get_parser(prog_name)
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

        if args.key is not None:
            query["key"] = args.key

        query["order"] = args.order
        query["limit"] = args.limit

        records = client.get("/api/v1/records", **query)
        # TODO: Record list API should provide timestamps
        columns = ("id", "playbook", "key", "type", "updated")
        # fmt: off
        return (
            columns, (
                [record[column] for column in columns]
                for record in records["results"]
            )
        )
        # fmt: on
