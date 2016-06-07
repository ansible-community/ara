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

from cliff.lister import Lister
from cliff.show import ShowOne
from ara import models
from ara.fields import Field

FIELDS = (
    Field('ID'),
    Field('Path'),
    Field('Playbook ID', 'playbook.id'),
)


class FileList(Lister):
    """Returns a list of files"""
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(FileList, self).get_parser(prog_name)
        g = parser.add_mutually_exclusive_group(required=True)
        g.add_argument(
            '--playbook', '-b',
            metavar='<playbook-id>',
            help='Show files associated with a specified playbook',
        )
        g.add_argument(
            '--all', '-a',
            action='store_true',
            help='List all files in the database',)
        return parser

    def take_action(self, args):
        files = (models.File.query
                 .order_by(models.File.path))

        if args.playbook:
            files = (files
                     .filter_by(playbook_id=args.playbook))

        return [[field.name for field in FIELDS],
                [[field(file_) for field in FIELDS]
                 for file_ in files]]


class FileShow(ShowOne):
    """Show details of a file"""
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(FileShow, self).get_parser(prog_name)
        parser.add_argument(
            'file',
            metavar='<file>',
            help='File id to show',
        )
        return parser

    def take_action(self, args):
        file_ = models.File.query.get(args.file)
        if file_ is None:
            raise RuntimeError('File %s could not be found' % args.file)

        return [[field.name for field in FIELDS],
                [field(file_) for field in FIELDS]]
