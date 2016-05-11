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


class ResultList(Lister):
    """Returns a list of results"""
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(ResultList, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        results = models.TaskResult.query.all()

        columns = ('id', 'task id', 'host id', 'changed', 'failed', 'skipped',
                   'unreachable', 'ignore errors', 'time start', 'time end')
        return (columns,
                (utils.get_object_properties(result, columns)
                 for result in results))


class ResultShow(ShowOne):
    """Show details of a result"""
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(ResultShow, self).get_parser(prog_name)
        parser.add_argument(
            'result_id',
            metavar='<result-id>',
            help='Result to show',
        )
        return parser

    def take_action(self, parsed_args):
        result = models.TaskResult.query.get(parsed_args.result_id)

        if hasattr(result, '_sa_instance_state'):
            delattr(result, '_sa_instance_state')

        return zip(*sorted(six.iteritems(result.__dict__)))
