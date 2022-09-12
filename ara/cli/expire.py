# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# See https://github.com/ansible-community/ara/issues/26 for rationale on expiring

import logging
import os
import sys
from datetime import datetime, timedelta

from cliff.command import Command

from ara.cli.base import global_arguments
from ara.clients.utils import get_client


class ExpireObjects(Command):
    """Expires objects that have been in the running state for too long"""

    log = logging.getLogger(__name__)
    expired = 0

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser = global_arguments(parser)
        # fmt: off
        parser.add_argument(
            "--hours",
            type=int,
            default=24,
            help="Expires objects that have been running state for this many hours (default: 24)"
        )
        parser.add_argument(
            "--order",
            metavar="<order>",
            default="started",
            help=(
                "Orders objects by a field ('id', 'created', 'updated', 'started', 'ended')\n"
                "Defaults to 'started' descending so the oldest objects would be expired first.\n"
                "The order can be reversed by using '-': ara expire --order=-started"
            ),
        )
        parser.add_argument(
            "--limit",
            metavar="<limit>",
            default=os.environ.get("ARA_CLI_LIMIT", 200),
            help=("Only expire the first <limit> determined by the ordering. Defaults to ARA_CLI_LIMIT or 200.")
        )
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Confirm expiration of objects, otherwise runs without expiring any objects",
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

        if not args.confirm:
            self.log.info("--confirm was not specified, no objects will be expired")

        query = dict(status="running")
        # generate a timestamp from n days ago in a format we can query the API with
        # ex: 2019-11-21T00:57:41.702229
        query["updated_before"] = (datetime.now() - timedelta(hours=args.hours)).isoformat()
        query["order"] = args.order
        query["limit"] = args.limit

        endpoints = ["/api/v1/playbooks", "/api/v1/plays", "/api/v1/tasks"]
        for endpoint in endpoints:
            objects = client.get(endpoint, **query)
            self.log.info("Found %s objects matching query on %s" % (objects["count"], endpoint))
            # TODO: Improve client validation and exception handling
            if "count" not in objects:
                # If we didn't get an answer we can parse, it's probably due to an error 500, 403, 401, etc.
                # The client would have logged the error.
                self.log.error(
                    "Client failed to retrieve results, see logs for ara.clients.offline or ara.clients.http."
                )
                sys.exit(1)

            for obj in objects["results"]:
                link = "%s/%s" % (endpoint, obj["id"])
                if not args.confirm:
                    self.log.info(
                        "Dry-run: %s would have been expired, status is running since %s" % (link, obj["updated"])
                    )
                else:
                    self.log.info("Expiring %s, status is running since %s" % (link, obj["updated"]))
                    client.patch(link, status="expired")
                    self.expired += 1

        self.log.info("%s objects expired" % self.expired)
