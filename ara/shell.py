#  Copyright (c) 2018 Red Hat, Inc.
#
#  This file is part of ARA Records Ansible.
#
#  ARA is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  ARA is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with ARA.  If not, see <http://www.gnu.org/licenses/>.

import logging
import sys

from ara import __version__
from ara.webapp import create_app
from cliff.app import App
from cliff.commandmanager import CommandManager
from flask import current_app


log = logging.getLogger('ara.shell')


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
        log.debug('initialize_app')

    def prepare_to_run_command(self, cmd):
        log.debug('prepare_to_run_command: %s', cmd.__class__.__name__)

        # Note: cliff uses self.app for itself, this gets folded back into
        # self.app.ara
        self.ara = create_app()
        if not current_app:
            self.ara_context = self.ara.app_context()
            self.ara_context.push()

    def clean_up(self, cmd, result, err):
        log.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            log.debug('got an error: %s', err)

        self.ara_context.pop()


def main(argv=sys.argv[1:]):
    aracli = AraCli()
    return aracli.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
