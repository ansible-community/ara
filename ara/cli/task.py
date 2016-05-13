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

    def take_action(self, parsed_args):
        tasks = (models.Task.query
                 .join(models.Play)
                 .join(models.Playbook)
                 .filter(models.Task.play_id == models.Play.id)
                 .filter(models.Task.playbook_id == models.Playbook.id))

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

    def take_action(self, parsed_args):
        task = models.Task.query.get(parsed_args.task_id)

        return utils.fields_from_object(
            FIELDS, task,
            xforms={
                'Playbook': lambda p: '{0} ({1})'.format(p.path, p.id),
                'Play': lambda p: '{0} ({1})'.format(p.name, p.id),
            })
