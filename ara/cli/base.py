# Copyright (c) 2020 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
import os
import sys

import pbr.version
from cliff.app import App
from cliff.commandmanager import CommandManager

CLIENT_VERSION = pbr.version.VersionInfo("ara").release_string()
log = logging.getLogger(__name__)


def global_arguments(parser):
    # fmt: off
    parser.add_argument(
        "--client",
        metavar="<client>",
        default=os.environ.get("ARA_API_CLIENT", "offline"),
        help=("API client to use, defaults to ARA_API_CLIENT or 'offline'"),
    )
    parser.add_argument(
        "--server",
        metavar="<url>",
        default=os.environ.get("ARA_API_SERVER", "http://127.0.0.1:8000"),
        help=("API server endpoint if using http client, defaults to ARA_API_SERVER or 'http://127.0.0.1:8000'"),
    )
    parser.add_argument(
        "--timeout",
        metavar="<seconds>",
        default=os.environ.get("ARA_API_TIMEOUT", 30),
        help=("Timeout for requests to API server, defaults to ARA_API_TIMEOUT or 30"),
    )
    parser.add_argument(
        "--username",
        metavar="<username>",
        default=os.environ.get("ARA_API_USERNAME", None),
        help=("API server username for authentication, defaults to ARA_API_USERNAME or None"),
    )
    parser.add_argument(
        "--password",
        metavar="<password>",
        default=os.environ.get("ARA_API_PASSWORD", None),
        help=("API server password for authentication, defaults to ARA_API_PASSWORD or None"),
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        default=os.environ.get("ARA_API_INSECURE", False),
        help=("Ignore SSL certificate validation, defaults to ARA_API_INSECURE or False"),
    )
    # fmt: on
    return parser


class AraCli(App):
    def __init__(self):
        super(AraCli, self).__init__(
            description="A CLI client to query ARA API servers",
            version=CLIENT_VERSION,
            command_manager=CommandManager("ara.cli"),
            deferred_help=True,
        )

    def build_option_parser(self, description, version):
        parser = super(AraCli, self).build_option_parser(description, version)
        return parser

    def initialize_app(self, argv):
        log.debug("initialize_app")

    def prepare_to_run_command(self, cmd):
        log.debug("prepare_to_run_command: %s", cmd.__class__.__name__)

    def clean_up(self, cmd, result, err):
        log.debug("clean_up %s", cmd.__class__.__name__)
        if err:
            log.debug("got an error: %s", err)


def main(argv=sys.argv[1:]):
    aracli = AraCli()
    return aracli.run(argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
