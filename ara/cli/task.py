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
    Field('Path'),
    Field('Line', 'lineno'),
    Field('Action'),
    Field('Time Start'),
    Field('Duration'),
)

SHOW_FIELDS = (
    Field('ID'),
    Field('Name'),
    Field('Playbook ID', 'playbook.id'),
    Field('Playbook Path', 'playbook.path'),
    Field('Play ID', 'play.id'),
    Field('Play Name', 'play.name'),
    Field('Path'),
    Field('Line', 'lineno'),
    Field('Action'),
    Field('Time Start'),
    Field('Time End'),
    Field('Duration'),
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
            help='Playbook from which to list tasks')
        g.add_argument(
            '--play', '-p',
            metavar='<play-id>',
            help='Play from which to list tasks')
        g.add_argument(
            '--all', '-a',
            action='store_true',
            help='List all tasks in the database')
        return parser

    def take_action(self, args):
        tasks = (models.Task.query
                 .join(models.Play)
                 .join(models.Playbook)
                 .filter(models.Task.play_id == models.Play.id)
                 .filter(models.Task.playbook_id == models.Playbook.id)
                 .order_by(models.Task.time_start, models.Task.sortkey))

        if args.play:
            tasks = (tasks
                     .filter(models.Task.play_id == args.play))
        elif args.playbook:
            tasks = (tasks
                     .filter(models.Task.playbook_id == args.playbook))

        return [[field.name for field in LIST_FIELDS],
                [[field(task) for field in LIST_FIELDS]
                 for task in tasks]]


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

        return [[field.name for field in SHOW_FIELDS],
                [field(task) for field in SHOW_FIELDS]]
