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
    """ Returns a list of plays """
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
            plays = plays.filter(models.Play.playbook_id == args.playbook)

        return [[field.name for field in LIST_FIELDS],
                [[field(play) for field in LIST_FIELDS]
                 for play in plays]]


class PlayShow(ShowOne):
    """ Show details of a play """
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
            raise RuntimeError('Play %s could not be found' % args.play_id)

        return [[field.name for field in SHOW_FIELDS],
                [field(play) for field in SHOW_FIELDS]]
