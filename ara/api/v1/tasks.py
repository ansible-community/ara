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
from ara.api.v1.results import ResultRestApi
from ara.db.models import db
from ara.db.models import File
from ara.db.models import Play
from ara.db.models import Task

from datetime import datetime
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

BASE_FIELDS = {
    'id': fields.Integer,
    'href': fields.Url('tasks.taskrestapi')
}

DETAIL_FIELDS = {
    'name': api_utils.Encoded,
    'action': fields.String,
    'lineno': fields.Integer,
    'tags': fields.Raw,
    'handler': fields.Boolean,
    'started': fields.DateTime(dt_format='iso8601'),
    'ended': fields.DateTime(dt_format='iso8601'),
    'results': api_utils.ResourceUrl('tasks.taskrestapi',
                                     resource='results'),
    'playbook': fields.Nested({
        'id': fields.Integer,
        'href': fields.Url('playbooks.playbookrestapi')
    }),
    'play': fields.Nested({
        'id': fields.Integer,
        'href': fields.Url('plays.playrestapi')
    }),
    'file': fields.Nested({
        'id': fields.Integer,
        'href': fields.Url('files.filerestapi')
    }),
}

TASK_FIELDS = BASE_FIELDS.copy()
TASK_FIELDS.update(DETAIL_FIELDS)


class TaskRestApi(Resource):
    """
    REST API for Tasks: api.v1.tasks
    """
    def post(self):
        """
        Creates a task with the provided arguments
        """
        parser = self._post_parser()
        args = parser.parse_args()

        # Validate and retrieve the play reference
        play = Play.query.get(args.play_id)
        if not play:
            abort(404,
                  message="Play {} doesn't exist".format(args.play_id),
                  help=api_utils.help(parser.args, TASK_FIELDS))

        # Validate and retrieve the file reference
        file_ = File.query.get(args.file_id)
        if not file_:
            abort(404,
                  message="File {} doesn't exist".format(args.file_id),
                  help=api_utils.help(parser.args, TASK_FIELDS))

        started = args.started
        if not started:
            started = datetime.utcnow()

        task = Task(
            playbook=play.playbook,
            play=play,
            file=file_,
            name=args.name,
            action=args.action,
            lineno=args.lineno,
            tags=args.tags,
            handler=args.handler,
            started=started,
            ended=args.ended
        )
        db.session.add(task)
        db.session.commit()

        return self.get(id=task.id)

    def patch(self):
        """
        Updates provided parameters for a task
        """
        parser = self._patch_parser()
        args = parser.parse_args()

        task = Task.query.get(args.id)
        if not task:
            abort(404, message="Task {} doesn't exist".format(args.id),
                  help=api_utils.help(parser.args, TASK_FIELDS))

        keys = ['name', 'action', 'lineno', 'tags', 'handler', 'started',
                'ended']
        updates = 0
        for key in keys:
            if getattr(args, key) is not None:
                updates += 1
                setattr(task, key, getattr(args, key))
        if not updates:
            abort(400, message="No parameters to update provided",
                  help=api_utils.help(parser.args, TASK_FIELDS))

        db.session.add(task)
        db.session.commit()

        return self.get(id=task.id)

    def get(self, id=None, playbook_id=None, play_id=None):
        """
        Retrieves one or many tasks based on the request and the query
        """
        parser = self._get_parser()
        args = parser.parse_args()

        if id is not None or ('id' in args and args['id'] is not None):
            id = id or args['id']
            task = _find_tasks(id=id)
            if task is None:
                abort(404, message="Task {} doesn't exist".format(id),
                      help=api_utils.help(parser.args, TASK_FIELDS))

            return marshal(task, TASK_FIELDS)

        # TODO: I don't particularly like this bit, improve it ?
        # _find_results does filter for None so it's safe but...
        if playbook_id is not None or play_id is not None:
            tasks = _find_tasks(playbook_id=playbook_id,
                                play_id=play_id)
            return marshal(tasks, BASE_FIELDS)

        tasks = _find_tasks(**args)
        if not tasks:
            abort(404, message="No tasks found for this query",
                  help=api_utils.help(parser.args, TASK_FIELDS))

        return marshal(tasks, BASE_FIELDS)

    @staticmethod
    def _post_parser():
        parser = reqparse.RequestParser()
        parser.add_argument(
            'file_id', dest='file_id',
            type=int,
            location='json',
            required=False,
            help='The file_id of the task'
        )
        parser.add_argument(
            'play_id', dest='play_id',
            type=int,
            location='json',
            required=True,
            help='The play_id of the task'
        )
        parser.add_argument(
            'name', dest='name',
            type=api_utils.encoded_input,
            location='json',
            required=True,
            help='The name of the task'
        )
        parser.add_argument(
            'action', dest='action',
            type=str,
            location='json',
            required=True,
            help='The action of the task'
        )
        parser.add_argument(
            'lineno', dest='lineno',
            type=int,
            location='json',
            required=False,
            help='The line number from the action of the task'
        )
        parser.add_argument(
            'tags', dest='tags',
            type=list,
            location='json',
            required=False,
            help='The tags of the task'
        )
        parser.add_argument(
            'handler', dest='handler',
            type=inputs.boolean,
            location='json',
            required=False,
            default=False,
            help='If the task is a handler'
        )
        parser.add_argument(
            'started', dest='started',
            type=inputs.datetime_from_iso8601,
            location='json',
            required=False,
            help='Timestamp for the start of the task (ISO8601)'
        )
        parser.add_argument(
            'ended', dest='ended',
            type=inputs.datetime_from_iso8601,
            location='json',
            required=False,
            help='Timestamp for the end of the task (ISO8601)'
        )
        return parser

    @staticmethod
    def _patch_parser():
        parser = reqparse.RequestParser()
        parser.add_argument(
            'id', dest='id',
            type=int,
            location='json',
            required=True,
            help='The id of the task'
        )
        parser.add_argument(
            'name', dest='name',
            type=api_utils.encoded_input,
            location='json',
            required=False,
            help='The name of the task'
        )
        parser.add_argument(
            'action', dest='action',
            type=str,
            location='json',
            required=False,
            help='The action of the task'
        )
        parser.add_argument(
            'lineno', dest='lineno',
            type=int,
            location='json',
            required=False,
            help='The line number from the action of the task'
        )
        parser.add_argument(
            'tags', dest='tags',
            type=list,
            location='json',
            required=False,
            help='The tags of the task'
        )
        parser.add_argument(
            'handler', dest='handler',
            type=inputs.boolean,
            location='json',
            required=False,
            help='If the task is a handler'
        )
        parser.add_argument(
            'started', dest='started',
            type=inputs.datetime_from_iso8601,
            location='json',
            required=False,
            help='Timestamp for the start of the task (ISO8601)'
        )
        parser.add_argument(
            'ended', dest='ended',
            type=inputs.datetime_from_iso8601,
            location='json',
            required=False,
            help='Timestamp for the end of the task (ISO8601)'
        )
        return parser

    @staticmethod
    def _get_parser():
        parser = reqparse.RequestParser()
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
            type=api_utils.encoded_input,
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
            help='Search with the lineno of a task'
        )
        parser.add_argument(
            'tags', dest='tags',
            type=list,
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
                u"%{0}%".format(kwargs['name'])
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
            kwargs['before'] < Task.started
        )

    if 'after' in kwargs and kwargs['after'] is not None:
        query = query.filter(
            kwargs['after'] > Task.started
        )

    return query.order_by(Task.id.asc()).all()


api.add_resource(TaskRestApi, '', '/<int:id>')
api.add_resource(ResultRestApi, '/<int:task_id>/results')
