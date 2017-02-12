#   Copyright 2017 Red Hat, Inc. All Rights Reserved.
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

import logging

from cliff.lister import Lister
from cliff.show import ShowOne
from ara import models
from ara.fields import Field

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
    """Returns a list of recorded key/value pairs"""
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
        data = (models.Data.query
                .order_by(models.Data.key))

        if args.playbook:
            data = (data
                    .filter_by(playbook_id=args.playbook))

        return [[field.name for field in LIST_FIELDS],
                [[field(key) for field in LIST_FIELDS]
                 for key in data]]


class DataShow(ShowOne):
    """Show details of a recorded key/value pair"""
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
                data = (models.Data.query
                        .filter_by(id=args.key).one())
        except (models.NoResultFound, models.MultipleResultsFound):
            raise RuntimeError('Key %s could not be found' % args.key)

        return [[field.name for field in SHOW_FIELDS],
                [field(data) for field in SHOW_FIELDS]]
