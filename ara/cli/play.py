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
    Field('Name'),
    Field('Playbook', 'playbook.path'),
    Field('Time Start'),
    Field('Duration'),
)

SHOW_FIELDS = (
    Field('ID'),
    Field('Name'),
    Field('Playbook ID', 'playbook.id'),
    Field('Playbook Path', 'playbook.path'),
    Field('Time Start'),
    Field('Time End'),
    Field('Duration'),
)


class PlayList(Lister):
    """Returns a list of plays"""
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(PlayList, self).get_parser(prog_name)
        g = parser.add_mutually_exclusive_group(required=True)
        g.add_argument(
            '--playbook', '-b',
            metavar='<playbook-id>',
            help='Show plays from specified playbook',
        )
        g.add_argument(
            '--all', '-a',
            action='store_true',
            help='Show all plays in database')
        return parser

    def take_action(self, args):
        plays = (models.Play.query
                 .join(models.Playbook)
                 .filter(models.Play.playbook_id == models.Playbook.id)
                 .order_by(models.Play.time_start, models.Play.sortkey))

        if args.playbook:
            plays = (plays
                     .filter(models.Play.playbook_id == args.playbook))

        return [[field.name for field in LIST_FIELDS],
                [[field(play) for field in LIST_FIELDS]
                 for play in plays]]


class PlayShow(ShowOne):
    """Show details of a play"""
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(PlayShow, self).get_parser(prog_name)
        parser.add_argument(
            'play_id',
            metavar='<play-id>',
            help='Play to show',
        )
        return parser

    def take_action(self, args):
        play = models.Play.query.get(args.play_id)
        if play is None:
            raise RuntimeError('Play %s could not be found' %
                               args.play_id)

        return [[field.name for field in SHOW_FIELDS],
                [field(play) for field in SHOW_FIELDS]]
