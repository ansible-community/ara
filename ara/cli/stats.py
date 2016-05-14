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
from ara import models, utils

FIELDS = (
    ('ID',),
    ('Host', 'host.name'),
    ('Playbook',),
    ('Changed',),
    ('Failed',),
    ('Ok',),
    ('Skipped',),
    ('Unreachable',),
)


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
                 .filter(models.Stats.host_id == models.Host.id))

        return utils.fields_from_iter(
            FIELDS, stats,
            xforms={
                'Playbook': lambda p: p.path,
            })


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

    def take_action(self, parsed_args):
        stats = models.Stats.query.get(parsed_args.stats_id)
        return utils.fields_from_object(
            FIELDS, stats,
            xforms={
                'Playbook': (lambda p: '{0} ({1})'.format(p.path, p.id)),
            })
