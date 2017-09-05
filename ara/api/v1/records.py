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
from ara.db.models import Record
from ara.db.models import Playbook

from flask import Blueprint
from flask_restful import Api
from flask_restful import abort
from flask_restful import fields
from flask_restful import marshal
from flask_restful import reqparse
from flask_restful import Resource

blueprint = Blueprint('records', __name__)
api = Api(blueprint)

RECORD_FIELDS = {
    'id': fields.Integer,
    'key': fields.String,
    'value': fields.Raw,
    'type': fields.String,
    'playbook': fields.Nested({
        'id': fields.Integer,
        'href': fields.Url('playbooks.playbookrestapi')
    }),
}


class RecordRestApi(Resource):
    """
    REST API for Records: api.v1.records
    """
    def post(self):
        """
        Creates a record with the provided arguments
        """
        parser = self._post_parser()
        args = parser.parse_args()

        # Validate and retrieve the playbook reference
        playbook = Playbook.query.get(args.playbook_id)
        if not playbook:
            abort(404,
                  message="Playbook {} doesn't exist".format(args.playbook_id),
                  help=api_utils.help(parser.args, RECORD_FIELDS))

        record = Record(
            playbook=playbook,
            key=args.key,
            value=args.value,
            type=args.type
        )
        db.session.add(record)
        db.session.commit()

        return self.get(id=record.id)

    def patch(self):
        """
        Updates provided parameters for a record
        """
        parser = self._patch_parser()
        args = parser.parse_args()

        record = Record.query.get(args.id)
        if not record:
            abort(404, message="Record {} doesn't exist".format(args.id),
                  help=api_utils.help(parser.args, RECORD_FIELDS))

        keys = ['key', 'value', 'type']
        updates = 0
        for key in keys:
            if getattr(args, key) is not None:
                updates += 1
                setattr(record, key, getattr(args, key))
        if not updates:
            abort(400, message="No parameters to update provided",
                  help=api_utils.help(parser.args, RECORD_FIELDS))

        db.session.add(record)
        db.session.commit()

        return self.get(id=record.id)

    def get(self, id=None):
        """
        Retrieves one or many records based on the request and the query
        """
        parser = self._get_parser()

        if id is not None:
            record = _find_records(id=id)
            if record is None:
                abort(404, message="Record {} doesn't exist".format(id),
                      help=api_utils.help(parser.args, RECORD_FIELDS))

            return marshal(record, RECORD_FIELDS)

        args = parser.parse_args()
        records = _find_records(**args)
        if not records:
            abort(404, message="No records found for this query",
                  help=api_utils.help(parser.args, RECORD_FIELDS))

        return marshal(records, RECORD_FIELDS)

    @staticmethod
    def _post_parser():
        parser = reqparse.RequestParser()
        parser.add_argument(
            'playbook_id', dest='playbook_id',
            type=int,
            location='json',
            required=True,
            help='The playbook_id for the record'
        )
        parser.add_argument(
            'key', dest='key',
            type=str,
            location='json',
            required=True,
            help='The key of the record'
        )
        parser.add_argument(
            'value', dest='value',
            type=api_utils.result_input,
            location='json',
            required=True,
            help='The value of the record'
        )
        parser.add_argument(
            'type', dest='type',
            type=str,
            location='json',
            choices=['text', 'url', 'json', 'list', 'dict'],
            required=False,
            default='text',
            help='The type of the record'
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
            help='The id of the record'
        )
        parser.add_argument(
            'key', dest='key',
            type=str,
            location='json',
            required=False,
            help='The key of the record'
        )
        parser.add_argument(
            'value', dest='value',
            type=api_utils.result_input,
            location='json',
            required=False,
            help='The value of the record'
        )
        parser.add_argument(
            'type', dest='type',
            type=str,
            location='json',
            choices=['text', 'url', 'json', 'list', 'dict'],
            required=False,
            default='text',
            help='The type of the record'
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
            help='Search with the id of a record'
        )
        parser.add_argument(
            'playbook_id', dest='playbook_id',
            type=int,
            location='values',
            required=False,
            help='Search records for a playbook id'
        )
        parser.add_argument(
            'key', dest='key',
            type=str,
            location='values',
            required=False,
            help='Search with the name of a key'
        )
        return parser


def _find_records(**kwargs):
    if 'id' in kwargs and kwargs['id'] is not None:
        return Record.query.get(kwargs['id'])

    query = Record.query
    if 'playbook_id' in kwargs and kwargs['playbook_id'] is not None:
        query = query.filter_by(playbook_id=kwargs['playbook_id'])

    if 'key' in kwargs and kwargs['key'] is not None:
        query = query.filter_by(key=kwargs['key'])

    return query.order_by(Record.id.desc()).all()


# Note (dmsimard)
# We are (unfortunately) routing /api/v1/<resource>/ instead of
# /api/v1/<resource> so that flask-frozen creates a <resource> directory
# instead of a <resource> file.
# In practice, the endpoint <resource> returns a 301 redirection to <resource>/
# when used on a live HTTP server.
api.add_resource(RecordRestApi, '/', '', '/<int:id>')
