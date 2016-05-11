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
        tasks = models.Task.query.all()

        columns = ('id', 'playbook id', 'play id', 'name', 'action', 'path',
                   'lineno', 'is handler', 'time start', 'time end')
        return (columns,
                (utils.get_object_properties(task, columns)
                 for task in tasks))


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

        if hasattr(task, '_sa_instance_state'):
            delattr(task, '_sa_instance_state')

        return zip(*sorted(six.iteritems(task.__dict__)))
