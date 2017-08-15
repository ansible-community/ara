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
from ara.db.models import Record

from flask import Blueprint
from flask_restful import Api
from flask_restful import abort
from flask_restful import fields
from flask_restful import marshal
from flask_restful import reqparse
from flask_restful import Resource
from flask_restful import inputs

blueprint = Blueprint('records', __name__)
api = Api(blueprint)

RECORD_FIELDS = {
    'id': fields.Integer,
    'playbook_id': fields.Integer,
    'key': fields.String,
    'value': fields.Raw,
    'type': fields.String
}


class RecordRestApi(Resource):
    """
    REST API for Records: api.v1.records
    """
    def get(self, id=None):
        parser = self._get_parser()

        if id is not None:
            record = _find_records(id=id)
            if record is None:
                abort(404, message="Record {} doesn't exist".format(id),
                      help=api_utils.help(parser.args, RECORD_FIELDS))

            return marshal(record, RECORD_FIELDS)

        args = parser.parse_args()
        if args.help:
            return api_utils.help(parser.args, RECORD_FIELDS)

        records = _find_records(**args)
        if not records:
            abort(404, message="No records found for this query",
                  help=api_utils.help(parser.args, RECORD_FIELDS))

        return marshal(records, RECORD_FIELDS)

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
