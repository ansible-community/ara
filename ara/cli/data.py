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

LIST_FIELDS = (
    Field('ID'),
    Field('Playbook ID', 'playbook.id'),
    Field('Playbook Path', 'playbook.path'),
    Field('Key'),
    Field('Type')
)

SHOW_FIELDS = (
    Field('ID'),
    Field('Playbook ID', 'playbook.id'),
    Field('Playbook Path', 'playbook.path'),
    Field('Key'),
    Field('Value'),
    Field('Type')
)


class DataList(Lister):
    """ Returns a list of recorded key/value pairs """
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(DataList, self).get_parser(prog_name)
        g = parser.add_mutually_exclusive_group(required=True)
        g.add_argument(
            '--playbook', '-b',
            metavar='<playbook-id>',
            help='Show key/value pairs associated with a specified playbook',
        )
        g.add_argument(
            '--all', '-a',
            action='store_true',
            help='List all key/value pairs in the database',)
        return parser

    def take_action(self, args):
        data = models.Data.query.order_by(models.Data.key)

        if args.playbook:
            data = data.filter_by(playbook_id=args.playbook)

        return [[field.name for field in LIST_FIELDS],
                [[field(key) for field in LIST_FIELDS]
                 for key in data]]


class DataShow(ShowOne):
    """ Show details of a recorded key/value pair """
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(DataShow, self).get_parser(prog_name)
        parser.add_argument(
            '--playbook', '-b',
            metavar='<playbook-id>',
            help='Show key associated with the given playbook',
        )
        parser.add_argument(
            'key',
            metavar='<key>',
            help='Key id (or name when using --playbook) to show',
        )
        return parser

    def take_action(self, args):
        try:
            if args.playbook:
                data = (models.Data.query
                        .filter_by(playbook_id=args.playbook)
                        .filter((models.Data.id == args.key) |
                                (models.Data.key == args.key)).one())
            else:
                data = models.Data.query.filter_by(id=args.key).one()
        except (models.NoResultFound, models.MultipleResultsFound):
            raise RuntimeError('Key %s could not be found' % args.key)

        return [[field.name for field in SHOW_FIELDS],
                [field(data) for field in SHOW_FIELDS]]
