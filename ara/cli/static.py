#   Copyright Red Hat, Inc. All Rights Reserved.
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

import logging
import os

from cliff.command import Command
from ara import app, freezer


class Generate(Command):
    """Generates a static tree of the web application"""
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Generate, self).get_parser(prog_name)
        parser.add_argument(
            'path',
            metavar='<path>',
            help='Path where the static files will be built in',
        )
        return parser

    def take_action(self, args):
        app.config['FREEZER_DESTINATION'] = os.path.abspath(args.path)
        self.log.warn('Generating static files at %s...',
                      args.path)
        freezer.freezer.freeze()

        print('Done.')
