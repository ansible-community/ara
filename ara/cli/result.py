# Copyright (c) 2020 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging

from cliff.lister import Lister

from ara.cli.base import global_arguments
from ara.clients.utils import get_client


class ResultList(Lister):
    """ Returns a list of results based on search queries """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(ResultList, self).get_parser(prog_name)
        parser = global_arguments(parser)
        # fmt: off
        # Result search arguments and ordering as per ara.api.filters.ResultFilter
        # TODO: non-exhaustive (searching for failed, ok, unreachable, etc.)
        parser.add_argument(
            "--playbook",
            metavar="<playbook_id>",
            default=None,
            help=("List results for a specified playbook id"),
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

        if args.changed:
            query["changed"] = args.changed

        query["ignore_errors"] = args.ignore_errors
        query["order"] = args.order
        query["limit"] = args.limit

        results = client.get("/api/v1/results", **query)
        columns = (
            "id",
            "status",
            "changed",
            "ignore_errors",
            "duration",
            "playbook",
            "play",
            "task",
            "host",
            "started",
        )
        # fmt: off
        return (
            columns, (
                [result[column] for column in columns]
                for result in results["results"]
            )
        )
        # fmt: on
