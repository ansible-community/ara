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
from ara.db.models import content_sha1
from ara.db.models import db
from ara.db.models import File
from ara.db.models import FileContent
from ara.db.models import NoResultFound
from ara.db.models import Playbook

from flask import Blueprint
from flask_restful import Api
from flask_restful import abort
from flask_restful import fields
from flask_restful import marshal
from flask_restful import reqparse
from flask_restful import Resource

blueprint = Blueprint('files', __name__)
api = Api(blueprint)

FILE_FIELDS = {
    'id': fields.Integer,
    'path': fields.String,
    'content': api_utils.Encoded(attribute='content.content'),
    'sha1': fields.String(attribute='content.sha1'),
    'is_playbook': fields.Boolean,
    'playbook': fields.Nested({
        'id': fields.Integer,
        'href': fields.Url('playbooks.playbookrestapi')
    }),
}


class FileRestApi(Resource):
    """
    REST API for Files: api.v1.files
    """
    def post(self):
        """
        Creates a file with the provided arguments
        """
        parser = self._post_parser()
        args = parser.parse_args()

        # Validate and retrieve the playbook reference
        playbook = Playbook.query.get(args.playbook_id)
        if not playbook:
            abort(404,
                  message="Playbook {} doesn't exist".format(args.playbook_id),
                  help=api_utils.help(parser.args, FILE_FIELDS))

        # If this is the playbook file, mark it as such
        is_playbook = False
        if playbook.path == args.path:
            is_playbook = True

        # Files are stored uniquely by path for a playbook, get it or create it
        try:
            file_ = File.query.filter_by(
                playbook_id=args.playbook_id,
                path=args.path
            ).one()
            return self.get(id=file_.id)
        except NoResultFound:
            pass

        # Files are stored uniquely by sha1, get it or create it
        sha1 = content_sha1(args.content)
        try:
            content = FileContent.query.filter_by(sha1=sha1).one()
        except NoResultFound:
            content = FileContent(content=args.content)

        file_ = File(
            playbook=playbook,
            path=args.path,
            is_playbook=is_playbook,
            content=content
        )

        db.session.add(file_)
        db.session.commit()

        return self.get(id=file_.id)

    def patch(self):
        """
        Updates provided parameters for a file
        """
        parser = self._patch_parser()
        args = parser.parse_args()

        file_ = File.query.get(args.id)
        if not file_:
            abort(404, message="File {} doesn't exist".format(args.id),
                  help=api_utils.help(parser.args, FILE_FIELDS))

        keys = ['path', 'content']
        updates = 0
        for key in keys:
            if getattr(args, key) is not None:
                updates += 1
                if key == 'content':
                    # Files are stored uniquely by sha1, get it or create it
                    sha1 = content_sha1(args.content)
                    try:
                        content = FileContent.query.filter_by(sha1=sha1).one()
                    except NoResultFound:
                        content = FileContent(content=args.content)
                    file_.content = content
                else:
                    setattr(file_, key, getattr(args, key))
        if not updates:
            abort(400, message="No parameters to update provided",
                  help=api_utils.help(parser.args, FILE_FIELDS))

        db.session.add(file_)
        db.session.commit()

        return self.get(id=file_.id)

    def get(self, id=None):
        """
        Retrieves one or many files based on the request and the query
        """
        parser = self._get_parser()

        if id is not None:
            file_ = _find_files(id=id)
            if file_ is None:
                abort(404, message="File {} doesn't exist".format(id),
                      help=api_utils.help(parser.args, FILE_FIELDS))

            return marshal(file_, FILE_FIELDS)

        args = parser.parse_args()
        files = _find_files(**args)
        if not files:
            abort(404, message='No files found for this query',
                  help=api_utils.help(parser.args, FILE_FIELDS))

        return marshal(files, FILE_FIELDS)

    @staticmethod
    def _post_parser():
        parser = reqparse.RequestParser()
        parser.add_argument(
            'playbook_id', dest='playbook_id',
            type=int,
            location='json',
            required=True,
            help='The playbook_id of the file'
        )
        parser.add_argument(
            'path', dest='path',
            type=str,
            location='json',
            required=True,
            help='The path of the file'
        )
        parser.add_argument(
            'content', dest='content',
            type=api_utils.encoded_input,
            location='json',
            required=True,
            help='The content of the file'
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
            help='The id of the file'
        )
        parser.add_argument(
            'path', dest='path',
            type=str,
            location='json',
            required=False,
            help='The path of the file'
        )
        parser.add_argument(
            'content', dest='content',
            type=api_utils.encoded_input,
            location='json',
            required=False,
            help='The content of the file'
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
        query = query.filter_by(is_playbook=kwargs['is_playbook'])

    return query.order_by(File.id.desc()).all()


# Note (dmsimard)
# We are (unfortunately) routing /api/v1/<resource>/ instead of
# /api/v1/<resource> so that flask-frozen creates a <resource> directory
# instead of a <resource> file.
# In practice, the endpoint <resource> returns a 301 redirection to <resource>/
# when used on a live HTTP server.
api.add_resource(FileRestApi, '/', '', '/<int:id>')
