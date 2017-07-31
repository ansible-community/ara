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

from ara import models
from ara.utils import fast_count
from flask import Blueprint
from flask import current_app
from flask import render_template

about = Blueprint('about', __name__)


@about.route('/')
def main():
    """ Returns the about page """
    if current_app.config['ARA_PLAYBOOK_OVERRIDE'] is not None:
        override = current_app.config['ARA_PLAYBOOK_OVERRIDE']
        files = (models.File.query
                 .filter(models.File.playbook_id.in_(override)))
        host_facts = (models.HostFacts.query
                      .join(models.Host)
                      .filter(models.Host.playbook_id.in_(override)))
        hosts = (models.Host.query
                 .filter(models.Host.playbook_id.in_(override)))
        playbooks = (models.Playbook.query
                     .filter(models.Playbook.id.in_(override)))
        records = (models.Data.query
                   .filter(models.Data.playbook_id.in_(override)))
        tasks = (models.Task.query
                 .filter(models.Task.playbook_id.in_(override)))
        task_results = (models.TaskResult.query
                        .join(models.Task)
                        .filter(models.Task.playbook_id.in_(override)))
    else:
        files = models.File.query
        host_facts = models.HostFacts.query
        hosts = models.Host.query
        playbooks = models.Playbook.query
        records = models.Data.query
        tasks = models.Task.query
        task_results = models.TaskResult.query

    return render_template('about.html',
                           active='about',
                           files=fast_count(files),
                           host_facts=fast_count(host_facts),
                           hosts=fast_count(hosts),
                           playbooks=fast_count(playbooks),
                           records=fast_count(records),
                           tasks=fast_count(tasks),
                           task_results=fast_count(task_results))
