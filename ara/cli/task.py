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


class TaskList(Lister):
    """Returns a list of tasks"""
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(TaskList, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        tasks = (models.Task.query
                 .join(models.Play)
                 .join(models.Playbook)
                 .filter(models.Task.play_id == models.Play.id)
                 .filter(models.Task.playbook_id == models.Playbook.id))

        fields = (
            ('ID',),
            ('Name',),
            ('Path',),
            ('Playbook', 'playbook.path'),
            ('Play', 'play.name'),
            ('Action',),
            ('Line', 'lineno',),
            ('Time Start',),
            ('Time End',),
        )

        return ([field[0] for field in fields],
                [[utils.get_field_attr(task, field)
                  for field in fields] for task in tasks])


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

        playbook = "{0} ({1})".format(task.playbook.path, task.playbook_id)
        play = "{0} ({1})".format(task.play.name, task.play_id)
        data = {
            'ID': task.id,
            'Name': task.name,
            'Path': task.path,
            'Playbook': playbook,
            'Play': play,
            'Action': task.action,
            'Line': task.lineno,
            'Time Start': task.time_start,
            'Time End': task.time_end
        }

        return zip(*sorted(six.iteritems(data)))
