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
from ara.db.models import Host

from flask import Blueprint
from flask_restful import Api
from flask_restful import abort
from flask_restful import fields
from flask_restful import marshal
from flask_restful import reqparse
from flask_restful import Resource

blueprint = Blueprint('hosts', __name__)
api = Api(blueprint)

HOST_FIELDS = {
    'id': fields.Integer,
    'playbook_id': fields.Integer,
    'facts': fields.Raw,
    'timestamp': fields.DateTime(dt_format='iso8601'),
    'name': api_utils.Encoded,
    'changed': fields.Integer,
    'failed': fields.Integer,
    'ok': fields.Integer,
    'skipped': fields.Integer,
    'unreachable': fields.Integer
}


class HostRestApi(Resource):
    """
    REST API for Hosts: api.v1.hosts
    """
    def get(self, id=None):
        parser = self._get_parser()

        if id is not None:
            host = _find_hosts(id=id)
            if host is None:
                abort(404, message="Host {} doesn't exist".format(id),
                      help=api_utils.help(parser.args, HOST_FIELDS))

            return marshal(host, HOST_FIELDS)

        args = parser.parse_args()
        hosts = _find_hosts(**args)
        if not hosts:
            abort(404, message='No hosts found for this query',
                  help=api_utils.help(parser.args, HOST_FIELDS))

        return marshal(hosts, HOST_FIELDS)

    @staticmethod
    def _get_parser():
        parser = reqparse.RequestParser()
        parser.add_argument(
            'id', dest='id',
            type=int,
            location='values',
            required=False,
            help='Search with the id of the host'
        )
        parser.add_argument(
            'playbook_id', dest='playbook_id',
            type=int,
            location='values',
            required=False,
            help='Search hosts for a playbook id'
        )
        parser.add_argument(
            'name', dest='name',
            type=api_utils.encoded_input,
            location='values',
            required=False,
            help='Search with the name (full or part) of a host'
        )
        return parser


def _find_hosts(**kwargs):
    if 'id' in kwargs and kwargs['id'] is not None:
        return Host.query.get(kwargs['id'])

    query = Host.query
    if 'playbook_id' in kwargs and kwargs['playbook_id'] is not None:
        query = query.filter_by(playbook_id=kwargs['playbook_id'])

    if 'name' in kwargs and kwargs['name'] is not None:
        query = query.filter(
            Host.name.like(
                "%{0}%".format(kwargs['name'])
            )
        )

    return query.order_by(Host.id.desc()).all()


# Note (dmsimard)
# We are (unfortunately) routing /api/v1/<resource>/ instead of
# /api/v1/<resource> so that flask-frozen creates a <resource> directory
# instead of a <resource> file.
# In practice, the endpoint <resource> returns a 301 redirection to <resource>/
# when used on a live HTTP server.
api.add_resource(HostRestApi, '/', '', '/<int:id>')
