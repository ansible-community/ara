#  Copyright (c) 2017 Red Hat, Inc.
#
#  This file is part of ARA: Ansible Run Analysis.
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

from ara.api.v1 import utils as api_utils
from ara.db.models import Result

from flask import Blueprint
from flask_restful import Api
from flask_restful import abort
from flask_restful import fields
from flask_restful import marshal
from flask_restful import reqparse
from flask_restful import Resource
from flask_restful import inputs

blueprint = Blueprint('results', __name__)
api = Api(blueprint)

RESULT_FIELDS = {
    'id': fields.Integer,
    'playbook_id': fields.Integer,
    'play_id': fields.Integer,
    'task_id': fields.Integer,
    'host_id': fields.Integer,
    'status': fields.String,
    'changed': fields.Boolean,
    'failed': fields.Boolean,
    'skipped': fields.Boolean,
    'unreachable': fields.Boolean,
    'ignore_errors': fields.Boolean,
    'result': fields.Raw,
    'started': fields.DateTime(dt_format='iso8601'),
    'ended': fields.DateTime(dt_format='iso8601')
}


class ResultRestApi(Resource):
    """
    REST API for Results: api.v1.results
    """
    def get(self, id=None):
        parser = self._get_parser()

        if id is not None:
            result = _find_results(id=id)
            if result is None:
                abort(404, message="Result {} doesn't exist".format(id),
                      help=api_utils.help(parser.args, RESULT_FIELDS))

            return marshal(result, RESULT_FIELDS)

        args = parser.parse_args()
        if args.help:
            return api_utils.help(parser.args, RESULT_FIELDS)

        results = _find_results(**args)
        if not results:
            abort(404, message="No results found for this query",
                  help=api_utils.help(parser.args, RESULT_FIELDS))

        return marshal(results, RESULT_FIELDS)

    @staticmethod
    def _get_parser():
        parser = reqparse.RequestParser()
        parser.add_argument(
            'help', dest='help',
            type=inputs.boolean,
            location='values',
            required=False,
            help='Returns list of arguments for this endpoint'
        )
        parser.add_argument(
            'id', dest='id',
            type=int,
            location='values',
            required=False,
            help='Search with the id of a result'
        )
        parser.add_argument(
            'playbook_id', dest='playbook_id',
            type=int,
            location='values',
            required=False,
            help='Search results for a playbook id'
        )
        parser.add_argument(
            'play_id', dest='play_id',
            type=int,
            location='values',
            required=False,
            help='Search results for a play id'
        )
        parser.add_argument(
            'task_id', dest='task_id',
            type=int,
            location='values',
            required=False,
            help='Search results for a task id'
        )
        parser.add_argument(
            'host_id', dest='host_id',
            type=int,
            location='values',
            required=False,
            help='Search results for a host id'
        )
        parser.add_argument(
            'status', dest='status',
            type=str,
            location='values',
            required=False,
            choices=['ok', 'failed', 'skipped', 'unreachable'],
            help='Search results by status'
        )
        parser.add_argument(
            'changed', dest='changed',
            type=inputs.boolean,
            location='values',
            required=False,
            help='Search results based on if they have changed or not'
        )
        parser.add_argument(
            'failed', dest='failed',
            type=inputs.boolean,
            location='values',
            required=False,
            help='Search results based on if they have failed or not'
        )
        parser.add_argument(
            'skipped', dest='skipped',
            type=inputs.boolean,
            location='values',
            required=False,
            help='Search results based on if they have been skipped or not'
        )
        parser.add_argument(
            'unreachable', dest='unreachable',
            type=inputs.boolean,
            location='values',
            required=False,
            help='Search results based on if they have been unreachable or not'
        )
        parser.add_argument(
            'ignore_errors', dest='ignore_errors',
            type=inputs.boolean,
            location='values',
            required=False,
            help='Search results based on if errors have been ignored or not'
        )
        # Full text searching in the result field ??
        parser.add_argument(
            'before', dest='before',
            type=inputs.datetime_from_iso8601,
            location='values',
            required=False,
            help='Search results that occurred before a timestamp (ISO8601)'
        )
        parser.add_argument(
            'after', dest='after',
            type=inputs.datetime_from_iso8601,
            location='values',
            required=False,
            help='Search results that occurred after a timestamp (ISO8601)'
        )
        return parser


def _find_results(**kwargs):
    if 'id' in kwargs and kwargs['id'] is not None:
        return Result.query.get(kwargs['id'])

    query = Result.query
    if 'playbook_id' in kwargs and kwargs['playbook_id'] is not None:
        query = query.filter_by(playbook_id=kwargs['playbook_id'])

    if 'play_id' in kwargs and kwargs['play_id'] is not None:
        query = query.filter_by(play_id=kwargs['play_id'])

    if 'task_id' in kwargs and kwargs['task_id'] is not None:
        query = query.filter_by(task_id=kwargs['task_id'])

    if 'host_id' in kwargs and kwargs['host_id'] is not None:
        query = query.filter_by(host_id=kwargs['host_id'])

    if 'status' in kwargs and kwargs['status'] is not None:
        query = query.filter_by(status=kwargs['status'])

    if 'changed' in kwargs and kwargs['changed'] is not None:
        query = query.filter_by(changed=kwargs['changed'])

    if 'failed' in kwargs and kwargs['failed'] is not None:
        query = query.filter_by(failed=kwargs['failed'])

    if 'skipped' in kwargs and kwargs['skipped'] is not None:
        query = query.filter_by(skipped=kwargs['skipped'])

    if 'unreachable' in kwargs and kwargs['unreachable'] is not None:
        query = query.filter_by(unreachable=kwargs['unreachable'])

    if 'ignore_errors' in kwargs and kwargs['ignore_errors'] is not None:
        query = query.filter_by(ignore_errors=kwargs['ignore_errors'])

    if 'before' in kwargs and kwargs['before'] is not None:
        query = query.filter(
            kwargs['before'] < Result.ended
        )

    if 'after' in kwargs and kwargs['after'] is not None:
        query = query.filter(
            kwargs['after'] > Result.ended
        )

    return query.order_by(Result.id.desc()).all()


# Note (dmsimard)
# We are (unfortunately) routing /api/v1/<resource>/ instead of
# /api/v1/<resource> so that flask-frozen creates a <resource> directory
# instead of a <resource> file.
# In practice, the endpoint <resource> returns a 301 redirection to <resource>/
# when used on a live HTTP server.
api.add_resource(ResultRestApi, '/', '', '/<int:id>')
