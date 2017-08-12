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
from ara.db.models import File

from flask import Blueprint
from flask_restful import Api
from flask_restful import abort
from flask_restful import fields
from flask_restful import marshal
from flask_restful import reqparse
from flask_restful import Resource
from flask_restful import inputs

blueprint = Blueprint('files', __name__)
api = Api(blueprint)

FILE_FIELDS = {
    'id': fields.Integer,
    'playbook_id': fields.Integer,
    'path': fields.String,
    'content': fields.String(attribute='content.content'),
    'sha1': fields.String(attribute='content.sha1'),
    'is_playbook': fields.Boolean,
}


class FileRestApi(Resource):
    """
    REST API for Files: api.v1.files
    """
    def get(self, id=None):
        parser = self._get_parser()

        if id is not None:
            file_ = _find_files(id=id)
            if file_ is None:
                abort(404, message="File {} doesn't exist".format(id),
                      help=api_utils.help(parser.args, FILE_FIELDS))

            return marshal(file_, FILE_FIELDS), 200

        args = parser.parse_args()
        if args.help:
            return api_utils.help(parser.args, FILE_FIELDS)

        files = _find_files(**args)
        if not files:
            abort(404, message='No files found for this query',
                  help=api_utils.help(parser.args, FILE_FIELDS))

        return marshal(files, FILE_FIELDS), 200

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
            help='Search with the id of the file'
        )
        parser.add_argument(
            'playbook_id', dest='playbook_id',
            type=int,
            location='values',
            required=False,
            help='Search files for a playbook id'
        )
        parser.add_argument(
            'path', dest='path',
            type=str,
            location='values',
            required=False,
            help='Search with the path (full or part) of a file'
        )
        parser.add_argument(
            'is_playbook', dest='is_playbook',
            type=inputs.boolean,
            location='values',
            required=False,
            help='Search for files that are playbook files'
        )
        return parser


def _find_files(**kwargs):
    if 'id' in kwargs and kwargs['id'] is not None:
        return File.query.get(kwargs['id'])

    query = File.query
    if 'playbook_id' in kwargs and kwargs['playbook_id'] is not None:
        query = query.filter_by(playbook_id=kwargs['playbook_id'])

    if 'path' in kwargs and kwargs['path'] is not None:
        query = query.filter(
            File.path.like(
                "%{0}%".format(kwargs['path'])
            )
        )

    if 'is_playbook' in kwargs and kwargs['is_playbook'] is not None:
        query = query.filter_by(complete=kwargs['is_playbook'])

    return query.order_by(File.id.desc()).all()


api.add_resource(FileRestApi, '', '/<int:id>')
