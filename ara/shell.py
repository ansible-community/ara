#   Copyright 2016 Red Hat, Inc. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import sys

from cliff.app import App
from cliff.commandmanager import CommandManager

from ara import __version__
from ara.config import *  # NOQA


class AraCli(App):
    """
    A CLI client to query ARA databases
    """
    def __init__(self):
        super(AraCli, self).__init__(
            description='A CLI client to query ARA databases',
            version=__version__,
            command_manager=CommandManager('ara.cli'),
            deferred_help=True)

    def build_option_parser(self, description, version):
        parser = super(AraCli, self).build_option_parser(description, version)

        # Global arguments
        # < None right now >

        return parser

    def initialize_app(self, argv):
        self.LOG.debug('initialize_app')

    def prepare_to_run_command(self, cmd):
        self.LOG.debug('prepare_to_run_command %s', cmd.__class__.__name__)

    def clean_up(self, cmd, result, err):
        self.LOG.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.LOG.debug('got an error: %s', err)


def main(argv=sys.argv[1:]):
    aracli = AraCli()
    return aracli.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
