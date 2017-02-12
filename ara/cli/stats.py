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
    """Returns a list of statistics"""
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
    """Show details of a statistic"""
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
            raise RuntimeError('Stats %s could not be found' %
                               args.stats_id)

        return [[field.name for field in SHOW_FIELDS],
                [field(stats) for field in SHOW_FIELDS]]
