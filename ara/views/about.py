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
from flask import current_app
from flask import render_template

from ara.db import models
from ara.utils import fast_count

about = Blueprint('about', __name__)


@about.route('/')
def main():
    """ Returns the about page """
    if current_app.config['ARA_PLAYBOOK_OVERRIDE'] is not None:
        override = current_app.config['ARA_PLAYBOOK_OVERRIDE']
        files = (models.File.query
                 .filter(models.File.playbook_id.in_(override)))
        hosts = (models.Host.query
                 .filter(models.Host.playbook_id.in_(override)))
        playbooks = (models.Playbook.query
                     .filter(models.Playbook.id.in_(override)))
        records = (models.Record.query
                   .filter(models.Record.playbook_id.in_(override)))
        tasks = (models.Task.query
                 .filter(models.Task.playbook_id.in_(override)))
        results = (models.Result.query
                   .join(models.Task)
                   .filter(models.Task.playbook_id.in_(override)))
    else:
        files = models.File.query
        hosts = models.Host.query
        playbooks = models.Playbook.query
        records = models.Record.query
        tasks = models.Task.query
        results = models.Result.query

    return render_template('about.html',
                           active='about',
                           files=fast_count(files),
                           hosts=fast_count(hosts),
                           playbooks=fast_count(playbooks),
                           records=fast_count(records),
                           tasks=fast_count(tasks),
                           results=fast_count(results))
