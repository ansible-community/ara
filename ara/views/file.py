#   Copyright 2017 Red Hat, Inc. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

from flask import render_template, abort, Blueprint, current_app
from ara import models

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
    """ Returns details of a file """
    file_ = (models.File.query.get(file_))
    if file_ is None:
        abort(404)

    return render_template('file.html', file_=file_)
