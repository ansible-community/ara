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
from ara.api.v1.files import FileRestApi
from ara.api.v1.hosts import HostRestApi
from ara.api.v1.plays import PlayRestApi
from ara.api.v1.records import RecordRestApi
from ara.api.v1.results import ResultRestApi
from ara.api.v1.tasks import TaskRestApi
from ara.db.models import db
from ara.db.models import Playbook

from datetime import datetime
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

BASE_FIELDS = {
    'id': fields.Integer,
    'href': fields.Url('playbooks.playbookrestapi')
}

DETAIL_FIELDS = {
    'path': fields.String,
    'ansible_version': fields.String,
    'completed': fields.Boolean,
    'started': fields.DateTime(dt_format='iso8601'),
    'ended': fields.DateTime(dt_format='iso8601'),
    'parameters': fields.Raw,
    'files': api_utils.ResourceUrl('playbooks.playbookrestapi',
                                   resource='files'),
    'hosts': api_utils.ResourceUrl('playbooks.playbookrestapi',
                                   resource='hosts'),
    'plays': api_utils.ResourceUrl('playbooks.playbookrestapi',
                                   resource='plays'),
    'records': api_utils.ResourceUrl('playbooks.playbookrestapi',
                                     resource='records'),
    'results': api_utils.ResourceUrl('playbooks.playbookrestapi',
                                     resource='results'),
    'tasks': api_utils.ResourceUrl('playbooks.playbookrestapi',
                                   resource='tasks')
}

PLAYBOOK_FIELDS = BASE_FIELDS.copy()
PLAYBOOK_FIELDS.update(DETAIL_FIELDS)


class PlaybookRestApi(Resource):
    """
    REST API for Playbooks: api.v1.playbooks
    """
    def post(self):
        """
        Creates a playbook with the provided arguments
        """
        parser = self._post_parser()
        args = parser.parse_args()

        started = args.started or datetime.utcnow()

        playbook = Playbook(
            path=args.path,
            ansible_version=args.ansible_version,
            parameters=args.parameters,
            completed=args.completed,
            started=started,
            ended=args.ended
        )
        db.session.add(playbook)
        db.session.commit()

        return self.get(id=playbook.id)

    def patch(self):
        """
        Updates provided parameters for a playbook
        """
        parser = self._patch_parser()
        args = parser.parse_args()

        playbook = Playbook.query.get(args.id)
        if not playbook:
            abort(404, message="Playbook {} doesn't exist".format(args.id),
                  help=api_utils.help(parser.args, PLAYBOOK_FIELDS))

        keys = ['path', 'ansible_version', 'parameters', 'completed',
                'started', 'ended']
        updates = 0
        for key in keys:
            if getattr(args, key) is not None:
                updates += 1
                setattr(playbook, key, getattr(args, key))
        if not updates:
            abort(400, message="No parameters to update provided",
                  help=api_utils.help(parser.args, PLAYBOOK_FIELDS))

        db.session.add(playbook)
        db.session.commit()

        return self.get(id=playbook.id)

    def get(self, id=None):
        """
        Retrieves one or many playbooks based on the request and the query
        """
        parser = self._get_parser()
        args = parser.parse_args()

        if id is not None or ('id' in args and args['id'] is not None):
            id = id or args['id']
            playbook = _find_playbooks(id=id)
            if playbook is None:
                abort(404, message="Playbook {} doesn't exist".format(id),
                      help=api_utils.help(parser.args, PLAYBOOK_FIELDS))
            return marshal(playbook, PLAYBOOK_FIELDS)

        playbooks = _find_playbooks(**args)
        if not playbooks:
            abort(404, message='No playbooks found for this query',
                  help=api_utils.help(parser.args, PLAYBOOK_FIELDS))

        return marshal(playbooks, BASE_FIELDS)

    @staticmethod
    def _post_parser():
        parser = reqparse.RequestParser()
        parser.add_argument(
            'path', dest='path',
            type=str,
            location='json',
            required=True,
            help='Path of the playbook'
        )
        parser.add_argument(
            'ansible_version', dest='ansible_version',
            type=str,
            location='json',
            required=True,
            help='Ansible version used when running the playbook'
        )
        parser.add_argument(
            'parameters', dest='parameters',
            type=dict,
            location='json',
            required=True,
            help='Ansible parameters and options when running the playbook'
        )
        parser.add_argument(
            'completed', dest='completed',
            type=inputs.boolean,
            location='json',
            default=False,
            required=False,
            help='Whether or not the playbook has completed'
        )
        parser.add_argument(
            'started', dest='started',
            type=inputs.datetime_from_iso8601,
            location='json',
            required=False,
            help='Timestamp for the start of the playbook run (ISO8601)'
        )
        parser.add_argument(
            'ended', dest='ended',
            type=inputs.datetime_from_iso8601,
            location='json',
            required=False,
            help='Timestamp for the end of the playbook run (ISO8601)'
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
            help='Id of the playbook'
        )
        parser.add_argument(
            'path', dest='path',
            type=str,
            location='json',
            required=False,
            help='Path of the playbook'
        )
        parser.add_argument(
            'ansible_version', dest='ansible_version',
            type=str,
            location='json',
            required=False,
            help='Ansible version used when running the playbook'
        )
        parser.add_argument(
            'parameters', dest='parameters',
            type=dict,
            location='json',
            required=False,
            help='Ansible parameters and options when running the playbook'
        )
        parser.add_argument(
            'completed', dest='completed',
            type=inputs.boolean,
            location='json',
            required=False,
            help='Whether or not the playbook has complete'
        )
        parser.add_argument(
            'started', dest='started',
            type=inputs.datetime_from_iso8601,
            location='json',
            required=False,
            help='Timestamp for the start of the playbook run (ISO8601)'
        )
        parser.add_argument(
            'ended', dest='ended',
            type=inputs.datetime_from_iso8601,
            location='json',
            required=False,
            help='Timestamp for the end of the playbook run (ISO8601)'
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
        query = query.filter_by(completed=kwargs['completed'])

    if 'before' in kwargs and kwargs['before'] is not None:
        query = query.filter(
            kwargs['before'] < Playbook.started
        )

    if 'after' in kwargs and kwargs['after'] is not None:
        query = query.filter(
            kwargs['after'] > Playbook.started
        )

    return query.order_by(Playbook.id.desc()).all()


api.add_resource(PlaybookRestApi, '', '/<int:id>')
api.add_resource(FileRestApi, '/<int:playbook_id>/files')
api.add_resource(HostRestApi, '/<int:playbook_id>/hosts')
api.add_resource(PlayRestApi, '/<int:playbook_id>/plays')
api.add_resource(RecordRestApi, '/<int:playbook_id>/records')
api.add_resource(ResultRestApi, '/<int:playbook_id>/results')
api.add_resource(TaskRestApi, '/<int:playbook_id>/tasks')
