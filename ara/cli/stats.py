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

COMMON_FIELDS = (
    Field('Changed'),
    Field('Failed'),
    Field('Ok'),
    Field('Skipped'),
    Field('Unreachable'),
)

LIST_FIELDS = (
    Field('ID'),
    Field('Host', 'host.name'),
    Field('Playbook', 'playbook.path'),
) + COMMON_FIELDS

SHOW_FIELDS = (
    Field('ID'),
    Field('Host', 'host.name'),
    Field('Playbook ID', 'playbook.id'),
    Field('Playbook Path', 'playbook.path'),
) + COMMON_FIELDS


class StatsList(Lister):
    """ Returns a list of statistics """
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(StatsList, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        stats = (models.Stats.query
                 .join(models.Playbook)
                 .join(models.Host)
                 .filter(models.Stats.playbook_id == models.Playbook.id)
                 .filter(models.Stats.host_id == models.Host.id)
                 .order_by(models.Playbook.time_start, models.Host.name))

        return [[field.name for field in LIST_FIELDS],
                [[field(stat) for field in LIST_FIELDS]
                 for stat in stats]]


class StatsShow(ShowOne):
    """ Show details of a statistic """
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(StatsShow, self).get_parser(prog_name)
        parser.add_argument(
            'stats_id',
            metavar='<stats-id>',
            help='Statistic to show',
        )
        return parser

    def take_action(self, args):
        stats = models.Stats.query.get(args.stats_id)
        if stats is None:
            raise RuntimeError('Stats %s could not be found' % args.stats_id)

        return [[field.name for field in SHOW_FIELDS],
                [field(stats) for field in SHOW_FIELDS]]
