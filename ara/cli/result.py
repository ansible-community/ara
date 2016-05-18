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
    ('Changed',),
    ('Failed',),
    ('Skipped',),
    ('Unreachable',),
    ('Ignore Errors',),
    ('Time Start',),
    ('Time End',),
)


class ResultList(Lister):
    """Returns a list of results"""
    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        results = (models.TaskResult.query
                   .join(models.Task)
                   .join(models.Host)
                   .filter(models.TaskResult.task_id == models.Task.id)
                   .filter(models.TaskResult.host_id == models.Host.id))

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

    def take_action(self, parsed_args):
        _fields = list(FIELDS)
        if parsed_args.long:
            _fields.append(('Result',))

        result = models.TaskResult.query.get(parsed_args.result_id)
        return utils.fields_from_object(
            _fields, result,
            xforms={
                'Task': lambda t: '{0} ({1})'.format(t.name, t.id),
                'Result': lambda r: utils.jinja_to_nice_json(
                    utils.jinja_from_json(r)),
            })
