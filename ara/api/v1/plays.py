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
from ara.db.models import Play

from flask import Blueprint
from flask_restful import Api
from flask_restful import fields
from flask_restful import marshal
from flask_restful import reqparse
from flask_restful import Resource
from flask_restful import inputs

blueprint = Blueprint('plays', __name__)
api = Api(blueprint)

PLAY_FIELDS = {
    'id': fields.Integer,
    'playbook_id': fields.Integer,
    'name': fields.String,
    'started': fields.DateTime(attribute='time_start',
                               dt_format='iso8601'),
    'ended': fields.DateTime(attribute='time_end',
                             dt_format='iso8601')
}


class PlayRestApi(Resource):
    """
    REST API for Plays: api.v1.plays
    """
    def get(self):
        parser = self._get_parser()
        args = parser.parse_args()
        if args.help:
            return api_utils.help(parser.args, PLAY_FIELDS)

        plays = _find_plays(**args)
        return marshal(plays, PLAY_FIELDS), 200

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
            help='Search with the id of a play'
        )
        parser.add_argument(
            'playbook_id', dest='playbook_id',
            type=int,
            location='values',
            required=False,
            help='Search plays for a playbook id'
        )
        parser.add_argument(
            'name', dest='name',
            type=str,
            location='values',
            required=False,
            help='Search with the name (full or part) of a play'
        )
        parser.add_argument(
            'before', dest='before',
            type=inputs.datetime_from_iso8601,
            location='values',
            required=False,
            help='Search plays that occurred before a timestamp (ISO8601)'
        )
        parser.add_argument(
            'after', dest='after',
            type=inputs.datetime_from_iso8601,
            location='values',
            required=False,
            help='Search plays that occurred after a timestamp (ISO8601)'
        )
        return parser


def _find_plays(**kwargs):
    if 'id' in kwargs and kwargs['id'] is not None:
        return [Play.query.get(kwargs['id'])]

    query = Play.query
    if 'playbook_id' in kwargs and kwargs['playbook_id'] is not None:
        query = query.filter_by(playbook_id=kwargs['playbook_id'])

    if 'name' in kwargs and kwargs['name'] is not None:
        query = query.filter(
            Play.name.like(
                "%{0}%".format(kwargs['name'])
            )
        )

    if 'before' in kwargs and kwargs['before'] is not None:
        query = query.filter(
            kwargs['before'] < Play.time_end
        )

    if 'after' in kwargs and kwargs['after'] is not None:
        query = query.filter(
            kwargs['after'] > Play.time_end
        )

    return query.order_by(Play.id.desc()).all()


api.add_resource(PlayRestApi, '')
