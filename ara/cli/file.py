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

from ara import models
from ara.fields import Field
from cliff.lister import Lister
from cliff.show import ShowOne

FIELDS = (
    Field('ID'),
    Field('Path'),
    Field('Playbook ID', 'playbook.id'),
)


class FileList(Lister):
    """ Returns a list of files """
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
        files = models.File.query.order_by(models.File.path)

        if args.playbook:
            files = files.filter_by(playbook_id=args.playbook)

        return [[field.name for field in FIELDS],
                [[field(file_) for field in FIELDS]
                 for file_ in files]]


class FileShow(ShowOne):
    """ Show details of a file """
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
