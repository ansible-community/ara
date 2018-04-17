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
    Field('Tags', template='{{ value | from_json | to_nice_json | safe }}'),
    Field('Time Start'),
    Field('Time End'),
    Field('Duration'),
)


class TaskList(Lister):
    """ Returns a list of tasks """
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
            tasks = tasks.filter(models.Task.play_id == args.play)
        elif args.playbook:
            tasks = tasks.filter(models.Task.playbook_id == args.playbook)

        return [[field.name for field in LIST_FIELDS],
                [[field(task) for field in LIST_FIELDS]
                 for task in tasks]]


class TaskShow(ShowOne):
    """ Show details of a task """
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
            raise RuntimeError('Task %s could not be found' % args.task_id)

        return [[field.name for field in SHOW_FIELDS],
                [field(task) for field in SHOW_FIELDS]]
