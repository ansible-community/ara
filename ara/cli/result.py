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
    ('Task',),
    ('Status', 'derived_status'),
    ('Ignore Errors',),
    ('Time Start',),
    ('Time End',),
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
            help='Playbook from which to list results',)
        g.add_argument(
            '--play', '-p',
            metavar='<play-id>',
            help='Play from which to list results',)
        g.add_argument(
            '--task', '-t',
            metavar='<task-id>',
            help='Task from which to list results',)
        g.add_argument(
            '--all', '-a',
            action='store_true',
            help='List all results in the database',)
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

        return utils.fields_from_iter(
            FIELDS, results,
            xforms={
                'Task': lambda t: t.name,
            })


class ResultShow(ShowOne):
    """Show details of a result"""
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(ResultShow, self).get_parser(prog_name)
        parser.add_argument(
            '--long', '-l',
            action='store_true',
            help='Show full JSON result',
        )
        parser.add_argument(
            'result_id',
            metavar='<result-id>',
            help='Result to show',
        )
        return parser

    def take_action(self, args):
        _fields = list(FIELDS)
        if args.long:
            _fields.append(('Result',))

        result = models.TaskResult.query.get(args.result_id)
        if result is None:
            raise RuntimeError('Result %s could not be found' %
                               args.result_id)

        return utils.fields_from_object(
            _fields, result,
            xforms={
                'Task': lambda t: '{0} ({1})'.format(t.name, t.id),
                'Result': lambda r: utils.format_json(r),
            })
