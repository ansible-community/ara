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
    Field('Name', 'task.name'),
    Field('Host', 'host.name'),
    Field('Action', 'task.action'),
    Field('Status', 'derived_status'),
    Field('Ignore Errors'),
    Field('Time Start'),
    Field('Duration'),
)

SHOW_FIELDS = (
    Field('ID'),
    Field('Name', 'task.name'),
    Field('Playbook ID', 'task.playbook.id'),
    Field('Playbook Path', 'task.playbook.path'),
    Field('Play ID', 'task.play.id'),
    Field('Play Name', 'task.play.name'),
    Field('Task ID', 'task.id'),
    Field('Task Name', 'task.name'),
    Field('Host', 'host.name'),
    Field('Action', 'task.action'),
    Field('Status', 'derived_status'),
    Field('Ignore Errors'),
    Field('Time Start'),
    Field('Time End'),
    Field('Duration'),
)

SHOW_FIELDS_LONG = SHOW_FIELDS + (
    Field('Result', 'result|from_json',
          template='{{ value | to_nice_json | safe }}'),
)

SHOW_FIELDS_RAW = SHOW_FIELDS + (
    Field('Result', 'result | from_json'),
)


class ResultList(Lister):
    """ Returns a list of results """
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(ResultList, self).get_parser(prog_name)

        g = parser.add_mutually_exclusive_group(required=True)
        g.add_argument(
            '--playbook', '-b',
            metavar='<playbook-id>',
            help='Playbook from which to list results')
        g.add_argument(
            '--play', '-p',
            metavar='<play-id>',
            help='Play from which to list results')
        g.add_argument(
            '--task', '-t',
            metavar='<task-id>',
            help='Task from which to list results')
        g.add_argument(
            '--all', '-a',
            action='store_true',
            help='List all results in the database')
        return parser

    def take_action(self, args):
        results = (models.TaskResult.query
                   .join(models.Task)
                   .join(models.Host)
                   .filter(models.TaskResult.task_id == models.Task.id)
                   .filter(models.TaskResult.host_id == models.Host.id)
                   .order_by(models.Task.time_start, models.Task.sortkey))

        if args.playbook:
            results = results.filter(models.Task.playbook_id == args.playbook)
        elif args.play:
            results = results.filter(models.Task.play_id == args.play)
        elif args.task:
            results = results.filter(models.TaskResult.task_id == args.task)

        return [[field.name for field in LIST_FIELDS],
                [[field(result) for field in LIST_FIELDS]
                 for result in results]]


class ResultShow(ShowOne):
    """ Show details of a result """
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(ResultShow, self).get_parser(prog_name)
        g = parser.add_mutually_exclusive_group()
        g.add_argument(
            '--long', '-l',
            dest='format',
            action='store_const',
            const='long',
            help='Show full result (serialized to json)',
        )

        # To understand why we have both --long and --raw, compare the
        # output of:
        #  ara result show ... -l -c Result -f json
        # With:
        #  ara result show ... -r -c Result -f json
        g.add_argument(
            '--raw', '-r',
            dest='format',
            action='store_const',
            const='raw',
            help='Show full result (raw result object)',
        )
        parser.add_argument(
            'result_id',
            metavar='<result-id>',
            help='Result to show',
        )
        return parser

    def take_action(self, args):
        result = models.TaskResult.query.get(args.result_id)
        if result is None:
            raise RuntimeError('Result %s could not be found' % args.result_id)

        if args.format == 'long':
            fields = SHOW_FIELDS_LONG
        elif args.format == 'raw':
            fields = SHOW_FIELDS_RAW
        else:
            fields = SHOW_FIELDS

        return [[field.name for field in fields],
                [field(result) for field in fields]]
