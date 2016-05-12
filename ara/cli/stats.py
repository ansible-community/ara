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
import six

from cliff.lister import Lister
from cliff.show import ShowOne
from ara import app, db, models, utils


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

        fields = (
            ('ID',),
            ('Host', 'host.name'),
            ('Playbook', 'playbook.path'),
            ('Changed',),
            ('Failed',),
            ('Ok',),
            ('Skipped',),
            ('Unreachable',),
        )

        return ([field[0] for field in fields],
                [[utils.get_field_attr(stat, field)
                  for field in fields] for stat in stats])


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

        host = "{0} ({1})".format(stats.host.name, stats.host_id)
        playbook = "{0} ({1})".format(stats.playbook.path, stats.playbook_id)
        data = {
            'ID': stats.id,
            'Host': host,
            'Playbook': playbook,
            'Changed': stats.changed,
            'Failed': stats.failed,
            'Ok': stats.ok,
            'Skipped': stats.skipped,
            'Unreachable': stats.unreachable
        }

        return zip(*sorted(six.iteritems(data)))
