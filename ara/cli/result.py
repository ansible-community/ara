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
    Field('Host', 'host.name'),
    Field('Action', 'task.action'),
    Field('Status', 'derived_status'),
    Field('Ignore Errors'),
    Field('Time Start'),
    Field('Duration'),
)

SHOW_FIELDS = (
    Field('ID'),
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
          template='{{value|to_nice_json|safe}}'),
)

SHOW_FIELDS_RAW = SHOW_FIELDS + (
    Field('Result', 'result|from_json'),
)


class ResultList(Lister):
    """Returns a list of results"""
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
            results = (results
                       .filter(models.Task.playbook_id == args.playbook))
        elif args.play:
            results = (results
                       .filter(models.Task.play_id == args.play))
        elif args.task:
            results = (results
                       .filter(models.TaskResult.task_id == args.task))

        return [[field.name for field in LIST_FIELDS],
                [[field(result) for field in LIST_FIELDS]
                 for result in results]]


class ResultShow(ShowOne):
    """Show details of a result"""
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
        #
        #  ara result show ... -l -c Result -f json
        #
        # With:
        #
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
            raise RuntimeError('Result %s could not be found' %
                               args.result_id)

        if args.format == 'long':
            fields = SHOW_FIELDS_LONG
        elif args.format == 'raw':
            fields = SHOW_FIELDS_RAW
        else:
            fields = SHOW_FIELDS

        return [[field.name for field in fields],
                [field(result) for field in fields]]
