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

from flask import Blueprint
from flask import abort
from flask import current_app
from flask import render_template

from ara.db import models

result = Blueprint('result', __name__)


@result.route('/')
def index():
    """
    This is not served anywhere in the web application.
    It is used explicitly in the context of generating static files since
    flask-frozen requires url_for's to crawl content.
    url_for's are not used with result.show_result directly and are instead
    dynamically generated through javascript for performance purposes.
    """
    if current_app.config['ARA_PLAYBOOK_OVERRIDE'] is not None:
        override = current_app.config['ARA_PLAYBOOK_OVERRIDE']
        results = (models.Result.query
                   .join(models.Task)
                   .filter(models.Task.playbook_id.in_(override)))
    else:
        results = models.Result.query.all()

    return render_template('result_index.html', results=results)


@result.route('/<item>/')
def show_result(item):
    result = models.Result.query.get(item)
    if result is None:
        abort(404)

    return render_template('result.html', result=result)
