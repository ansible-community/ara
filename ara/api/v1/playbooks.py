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
from ara.api.v1.files import FILE_FIELDS
from ara.api.v1.hosts import HOST_FIELDS
from ara.api.v1.plays import PLAY_FIELDS
from ara.api.v1.results import RESULT_FIELDS
from ara.api.v1.tasks import TASK_FIELDS
from ara.db.models import Playbook

from flask import Blueprint
from flask_restful import Api
from flask_restful import abort
from flask_restful import fields
from flask_restful import marshal
from flask_restful import reqparse
from flask_restful import Resource
from flask_restful import inputs

blueprint = Blueprint('playbooks', __name__)
api = Api(blueprint)

PLAYBOOK_FIELDS = {
    'id': fields.Integer,
    'path': fields.String,
    'ansible_version': fields.String,
    'completed': fields.Boolean(attribute='complete'),
    'started': fields.DateTime(attribute='time_start',
                               dt_format='iso8601'),
    'ended': fields.DateTime(attribute='time_end',
                             dt_format='iso8601'),
    'parameters': fields.Raw,
    'files': fields.List(fields.Nested(FILE_FIELDS)),
    'hosts': fields.List(fields.Nested(HOST_FIELDS)),
    'plays': fields.List(fields.Nested(PLAY_FIELDS)),
    'results': fields.List(fields.Nested(RESULT_FIELDS)),
    'tasks': fields.List(fields.Nested(TASK_FIELDS))
}


class PlaybookRestApi(Resource):
    """
    REST API for Playbooks: api.v1.playbooks
    """
    def get(self, id=None):
        parser = self._get_parser()

        if id is not None:
            playbook = _find_playbooks(id=id)
            if playbook is None:
                abort(404, message="Playbook {} doesn't exist".format(id),
                      help=api_utils.help(parser.args, PLAYBOOK_FIELDS))

            return marshal(playbook, PLAYBOOK_FIELDS), 200

        args = parser.parse_args()
        if args.help:
            return api_utils.help(parser.args, PLAYBOOK_FIELDS)

        playbooks = _find_playbooks(**args)
        if not playbooks:
            abort(404, message='No playbooks found for this query',
                  help=api_utils.help(parser.args, PLAYBOOK_FIELDS))

        return marshal(playbooks, PLAYBOOK_FIELDS), 200

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
            help='Search with the id of a playbook'
        )
        parser.add_argument(
            'path', dest='path',
            type=str,
            location='values',
            required=False,
            help='Search with the path (full or part) of a playbook'
        )
        parser.add_argument(
            'ansible_version', dest='ansible_version',
            type=str,
            location='values',
            required=False,
            help='Search with the Ansible version (full or part) of a playbook'
        )
        parser.add_argument(
            'completed', dest='completed',
            type=inputs.boolean,
            location='values',
            required=False,
            help='Search complete or incomplete playbook runs'
        )
        parser.add_argument(
            'before', dest='before',
            type=inputs.datetime_from_iso8601,
            location='values',
            required=False,
            help='Search playbooks that occurred before a timestamp (ISO8601)'
        )
        parser.add_argument(
            'after', dest='after',
            type=inputs.datetime_from_iso8601,
            location='values',
            required=False,
            help='Search playbooks that occurred after a timestamp (ISO8601)'
        )
        return parser


def _find_playbooks(**kwargs):
    if 'id' in kwargs and kwargs['id'] is not None:
        return Playbook.query.get(kwargs['id'])

    query = Playbook.query
    if 'path' in kwargs and kwargs['path'] is not None:
        query = query.filter(
            Playbook.path.like(
                "%{0}%".format(kwargs['path'])
            )
        )

    if 'ansible_version' in kwargs and kwargs['ansible_version'] is not None:
        query = query.filter(
            Playbook.ansible_version.like(
                "%{0}%".format(kwargs['ansible_version'])
            )
        )

    if 'completed' in kwargs and kwargs['completed'] is not None:
        query = query.filter_by(complete=kwargs['completed'])

    if 'before' in kwargs and kwargs['before'] is not None:
        query = query.filter(
            kwargs['before'] < Playbook.time_end
        )

    if 'after' in kwargs and kwargs['after'] is not None:
        query = query.filter(
            kwargs['after'] > Playbook.time_end
        )

    return query.order_by(Playbook.id.desc()).all()


api.add_resource(PlaybookRestApi, '', '/<int:id>')
