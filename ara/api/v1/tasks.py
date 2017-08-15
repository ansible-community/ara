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
from ara.db.models import Task

from flask import Blueprint
from flask_restful import Api
from flask_restful import abort
from flask_restful import fields
from flask_restful import marshal
from flask_restful import reqparse
from flask_restful import Resource
from flask_restful import inputs

blueprint = Blueprint('tasks', __name__)
api = Api(blueprint)

TASK_FIELDS = {
    'id': fields.Integer,
    'playbook_id': fields.Integer,
    'play_id': fields.Integer,
    'file_id': fields.Integer,
    'name': fields.String,
    'action': fields.String,
    'lineno': fields.Integer,
    'tags': fields.String,
    'handler': fields.Boolean,
    'started': fields.DateTime(dt_format='iso8601'),
    'ended': fields.DateTime(dt_format='iso8601'),
    'results': fields.List(fields.Nested({
        'id': fields.Integer,
        'href': fields.Url('results.resultrestapi')
    }))
}


class TaskRestApi(Resource):
    """
    REST API for Tasks: api.v1.tasks
    """
    def get(self, id=None):
        parser = self._get_parser()

        if id is not None:
            task = _find_tasks(id=id)
            if task is None:
                abort(404, message="Task {} doesn't exist".format(id),
                      help=api_utils.help(parser.args, TASK_FIELDS))

            return marshal(task, TASK_FIELDS)

        args = parser.parse_args()
        if args.help:
            return api_utils.help(parser.args, TASK_FIELDS)

        tasks = _find_tasks(**args)
        if not tasks:
            abort(404, message="No tasks found for this query",
                  help=api_utils.help(parser.args, TASK_FIELDS))

        return marshal(tasks, TASK_FIELDS)

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
            help='Search with the id of a task'
        )
        parser.add_argument(
            'playbook_id', dest='playbook_id',
            type=int,
            location='values',
            required=False,
            help='Search tasks for a playbook id'
        )
        parser.add_argument(
            'play_id', dest='play_id',
            type=int,
            location='values',
            required=False,
            help='Search tasks for a play id'
        )
        parser.add_argument(
            'file_id', dest='file_id',
            type=int,
            location='values',
            required=False,
            help='Search tasks for a file id'
        )
        parser.add_argument(
            'name', dest='name',
            type=str,
            location='values',
            required=False,
            help='Search with the name (full or part) of a task'
        )
        parser.add_argument(
            'action', dest='action',
            type=str,
            location='values',
            required=False,
            help='Search with the action (full or part) of a task'
        )
        parser.add_argument(
            'lineno', dest='lineno',
            type=int,
            location='values',
            required=False,
            help='Search with the name (full or part) of a task'
        )
        parser.add_argument(
            'tags', dest='tags',
            type=str,
            location='values',
            required=False,
            help='Search with the tags (full or part) of a task'
        )
        parser.add_argument(
            'handler', dest='handler',
            type=inputs.boolean,
            location='values',
            required=False,
            help="Search for a task that is or isn't a handler"
        )
        parser.add_argument(
            'before', dest='before',
            type=inputs.datetime_from_iso8601,
            location='values',
            required=False,
            help='Search tasks that occurred before a timestamp (ISO8601)'
        )
        parser.add_argument(
            'after', dest='after',
            type=inputs.datetime_from_iso8601,
            location='values',
            required=False,
            help='Search tasks that occurred after a timestamp (ISO8601)'
        )
        return parser


def _find_tasks(**kwargs):
    if 'id' in kwargs and kwargs['id'] is not None:
        return Task.query.get(kwargs['id'])

    query = Task.query
    if 'playbook_id' in kwargs and kwargs['playbook_id'] is not None:
        query = query.filter_by(playbook_id=kwargs['playbook_id'])

    if 'play_id' in kwargs and kwargs['play_id'] is not None:
        query = query.filter_by(play_id=kwargs['play_id'])

    if 'file_id' in kwargs and kwargs['file_id'] is not None:
        query = query.filter_by(file_id=kwargs['file_id'])

    if 'name' in kwargs and kwargs['name'] is not None:
        query = query.filter(
            Task.name.like(
                "%{0}%".format(kwargs['name'])
            )
        )

    if 'action' in kwargs and kwargs['action'] is not None:
        query = query.filter(
            Task.action.like(
                "%{0}%".format(kwargs['action'])
            )
        )

    if 'lineno' in kwargs and kwargs['lineno'] is not None:
        query = query.filter_by(lineno=kwargs['lineno'])

    if 'tags' in kwargs and kwargs['tags'] is not None:
        query = query.filter(
            Task.tags.like(
                "%{0}%".format(kwargs['tags'])
            )
        )

    if 'handler' in kwargs and kwargs['handler'] is not None:
        query = query.filter_by(handler=kwargs['handler'])

    if 'before' in kwargs and kwargs['before'] is not None:
        query = query.filter(
            kwargs['before'] < Task.ended
        )

    if 'after' in kwargs and kwargs['after'] is not None:
        query = query.filter(
            kwargs['after'] > Task.ended
        )

    return query.order_by(Task.id.desc()).all()


# Note (dmsimard)
# We are (unfortunately) routing /api/v1/<resource>/ instead of
# /api/v1/<resource> so that flask-frozen creates a <resource> directory
# instead of a <resource> file.
# In practice, the endpoint <resource> returns a 301 redirection to <resource>/
# when used on a live HTTP server.
api.add_resource(TaskRestApi, '/', '', '/<int:id>')
