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
from ara.db.models import Play
from ara.db.models import Playbook

from flask import Blueprint
from flask_restful import Api
from flask_restful import abort
from flask_restful import fields
from flask_restful import marshal
from flask_restful import reqparse
from flask_restful import Resource
from flask_restful import inputs

blueprint = Blueprint('plays', __name__)
api = Api(blueprint)

PLAY_FIELDS = {
    'id': fields.Integer,
    'name': api_utils.Encoded,
    'started': fields.DateTime(dt_format='iso8601'),
    'ended': fields.DateTime(dt_format='iso8601'),
    'playbook': fields.Nested({
        'id': fields.Integer,
        'href': fields.Url('playbooks.playbookrestapi')
    }),
    'results': fields.List(fields.Nested({
        'id': fields.Integer,
        'href': fields.Url('results.resultrestapi')
    })),
    'tasks': fields.List(fields.Nested({
        'id': fields.Integer,
        'href': fields.Url('tasks.taskrestapi')
    }))
}


class PlayRestApi(Resource):
    """
    REST API for Plays: api.v1.plays
    """
    def post(self):
        """
        Creates a play with the provided arguments
        """
        parser = self._post_parser()
        args = parser.parse_args()

        # Validate and retrieve the playbook reference
        playbook = Playbook.query.get(args.playbook_id)
        if not playbook:
            abort(404,
                  message="Playbook {} doesn't exist".format(args.playbook_id),
                  help=api_utils.help(parser.args, PLAY_FIELDS))

        play = Play(
            playbook=playbook,
            name=args.name,
            started=args.started,
            ended=args.ended
        )
        db.session.add(play)
        db.session.commit()

        return self.get(id=play.id)

    def patch(self):
        """
        Updates provided parameters for a play
        """
        parser = self._patch_parser()
        args = parser.parse_args()

        play = Play.query.get(args.id)
        if not play:
            abort(404, message="Play {} doesn't exist".format(args.id),
                  help=api_utils.help(parser.args, PLAY_FIELDS))

        keys = ['name', 'started', 'ended']
        updates = 0
        for key in keys:
            if getattr(args, key) is not None:
                updates += 1
                setattr(play, key, getattr(args, key))
        if not updates:
            abort(400, message="No parameters to update provided",
                  help=api_utils.help(parser.args, PLAY_FIELDS))

        db.session.add(play)
        db.session.commit()

        return self.get(id=play.id)

    def get(self, id=None):
        """
        Retrieves one or many plays based on the request and the query
        """
        parser = self._get_parser()

        if id is not None:
            play = _find_plays(id=id)
            if play is None:
                abort(404, message="Play {} doesn't exist".format(id),
                      help=api_utils.help(parser.args, PLAY_FIELDS))

            return marshal(play, PLAY_FIELDS)

        args = parser.parse_args()
        plays = _find_plays(**args)
        if not plays:
            abort(404, message="No plays found for this query",
                  help=api_utils.help(parser.args, PLAY_FIELDS))

        return marshal(plays, PLAY_FIELDS)

    @staticmethod
    def _post_parser():
        parser = reqparse.RequestParser()
        parser.add_argument(
            'playbook_id', dest='playbook_id',
            type=int,
            location='json',
            required=True,
            help='The playbook_id of the play'
        )
        parser.add_argument(
            'name', dest='name',
            type=api_utils.encoded_input,
            location='json',
            required=True,
            help='The name of the play'
        )
        parser.add_argument(
            'started', dest='started',
            type=inputs.datetime_from_iso8601,
            location='json',
            required=True,
            help='Timestamp for the start of the play (ISO8601)'
        )
        parser.add_argument(
            'ended', dest='ended',
            type=inputs.datetime_from_iso8601,
            location='json',
            required=False,
            help='Timestamp for the start of the play (ISO8601)'
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
            help='The id of the play'
        )
        parser.add_argument(
            'name', dest='name',
            type=api_utils.encoded_input,
            location='json',
            required=False,
            help='The name of the play'
        )
        parser.add_argument(
            'started', dest='started',
            type=inputs.datetime_from_iso8601,
            location='json',
            required=False,
            help='Timestamp for the start of the play (ISO8601)'
        )
        parser.add_argument(
            'ended', dest='ended',
            type=inputs.datetime_from_iso8601,
            location='json',
            required=False,
            help='Timestamp for the end of the play (ISO8601)'
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
            type=api_utils.encoded_input,
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
        return Play.query.get(kwargs['id'])

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
            kwargs['before'] < Play.started
        )

    if 'after' in kwargs and kwargs['after'] is not None:
        query = query.filter(
            kwargs['after'] > Play.started
        )

    return query.order_by(Play.id.desc()).all()


# Note (dmsimard)
# We are (unfortunately) routing /api/v1/<resource>/ instead of
# /api/v1/<resource> so that flask-frozen creates a <resource> directory
# instead of a <resource> file.
# In practice, the endpoint <resource> returns a 301 redirection to <resource>/
# when used on a live HTTP server.
api.add_resource(PlayRestApi, '/', '', '/<int:id>')
