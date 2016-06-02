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
    ('Name',),
    ('Path',),
    ('Playbook',),
    ('Play',),
    ('Action',),
    ('Line', 'lineno',),
    ('Time Start',),
    ('Time End',),
)


class TaskList(Lister):
    """Returns a list of tasks"""
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(TaskList, self).get_parser(prog_name)
        g = parser.add_mutually_exclusive_group(required=True)
        g.add_argument(
            '--playbook', '-b',
            metavar='<playbook-id>',
            help='Playbook from which to list tasks',)
        g.add_argument(
            '--play', '-p',
            metavar='<play-id>',
            help='Play from which to list tasks',)
        g.add_argument(
            '--all', '-a',
            action='store_true',
            help='List all tasks in the database',)
        return parser

    def take_action(self, args):
        tasks = (models.Task.query
                 .join(models.Play)
                 .join(models.Playbook)
                 .filter(models.Task.play_id == models.Play.id)
                 .filter(models.Task.playbook_id == models.Playbook.id))

        if args.play:
            tasks = (tasks
                     .filter(models.Task.play_id == args.play))
        elif args.playbook:
            tasks = (tasks
                     .filter(models.Task.playbook_id == args.playbook))

        return utils.fields_from_iter(
            FIELDS, tasks,
            xforms={
                'Playbook': lambda p: p.path,
                'Play': lambda p: p.name,
            })


class TaskShow(ShowOne):
    """Show details of a task"""
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(TaskShow, self).get_parser(prog_name)
        parser.add_argument(
            'task_id',
            metavar='<task-id>',
            help='Task to show',
        )
        return parser

    def take_action(self, args):
        task = models.Task.query.get(args.task_id)
        if task is None:
            raise RuntimeError('Task %s could not be found' %
                               args.task_id)

        return utils.fields_from_object(
            FIELDS, task,
            xforms={
                'Playbook': lambda p: '{0} ({1})'.format(p.path, p.id),
                'Play': lambda p: '{0} ({1})'.format(p.name, p.id),
            })
