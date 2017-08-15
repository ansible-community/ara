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
from ara.db.models import db
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
    'completed': fields.Boolean,
    'started': fields.DateTime(dt_format='iso8601'),
    'ended': fields.DateTime(dt_format='iso8601'),
    'parameters': fields.Raw,
    'files': fields.List(fields.Nested({
        'id': fields.Integer,
        'href': fields.Url('files.filerestapi')
    })),
    'hosts': fields.List(fields.Nested({
        'id': fields.Integer,
        'href': fields.Url('hosts.hostrestapi')
    })),
    'plays': fields.List(fields.Nested({
        'id': fields.Integer,
        'href': fields.Url('plays.playrestapi')
    })),
    'records': fields.List(fields.Nested({
        'id': fields.Integer,
        'href': fields.Url('records.recordrestapi')
    })),
    'results': fields.List(fields.Nested({
        'id': fields.Integer,
        'href': fields.Url('results.resultrestapi')
    })),
    'tasks': fields.List(fields.Nested({
        'id': fields.Integer,
        'href': fields.Url('tasks.taskrestapi')
    }))
}


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

        playbook = Playbook(
            path=args.path,
            ansible_version=args.ansible_version,
            parameters=args.parameters,
            completed=args.completed,
            started=args.started,
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

        if id is not None:
            playbook = _find_playbooks(id=id)
            if playbook is None:
                abort(404, message="Playbook {} doesn't exist".format(id),
                      help=api_utils.help(parser.args, PLAYBOOK_FIELDS))

            return marshal(playbook, PLAYBOOK_FIELDS)

        args = parser.parse_args()
        playbooks = _find_playbooks(**args)
        if not playbooks:
            abort(404, message='No playbooks found for this query',
                  help=api_utils.help(parser.args, PLAYBOOK_FIELDS))

        return marshal(playbooks, PLAYBOOK_FIELDS)

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
            required=True,
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
            kwargs['before'] < Playbook.ended
        )

    if 'after' in kwargs and kwargs['after'] is not None:
        query = query.filter(
            kwargs['after'] > Playbook.ended
        )

    return query.order_by(Playbook.id.desc()).all()


# Note (dmsimard)
# We are (unfortunately) routing /api/v1/<resource>/ instead of
# /api/v1/<resource> so that flask-frozen creates a <resource> directory
# instead of a <resource> file.
# In practice, the endpoint <resource> returns a 301 redirection to <resource>/
# when used on a live HTTP server.
api.add_resource(PlaybookRestApi, '/', '', '/<int:id>')
