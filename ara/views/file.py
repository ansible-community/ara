#  Copyright (c) 2018 Red Hat, Inc.
#
#  This file is part of ARA Records Ansible.
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

from ara import models
from flask import abort
from flask import Blueprint
from flask import current_app
from flask import render_template

file = Blueprint('file', __name__)


@file.route('/')
def index():
    """
    This is not served anywhere in the web application.
    It is used explicitly in the context of generating static files since
    flask-frozen requires url_for's to crawl content.
    url_for's are not used with file.show_file directly and are instead
    dynamically generated through javascript for performance purposes.
    """
    if current_app.config['ARA_PLAYBOOK_OVERRIDE'] is not None:
        override = current_app.config['ARA_PLAYBOOK_OVERRIDE']
        files = (models.File.query
                 .filter(models.File.playbook_id.in_(override)))
    else:
        files = models.File.query.all()

    return render_template('file_index.html', files=files)


@file.route('/<file_>/')
def show_file(file_):
    """
    Returns details of a file
    """
    file_ = (models.File.query.get(file_))
    if file_ is None:
        abort(404)

    return render_template('file.html', file_=file_)
