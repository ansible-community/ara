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

from flask import Blueprint
from flask import current_app
from flask import render_template

from ara import models
from ara.utils import fast_count

about = Blueprint('about', __name__)


@about.route('/')
def main():
    """ Returns the about page """
    files = models.File.query
    hosts = models.Host.query
    facts = models.HostFacts.query
    playbooks = models.Playbook.query
    records = models.Data.query
    tasks = models.Task.query
    results = models.TaskResult.query

    if current_app.config['ARA_PLAYBOOK_OVERRIDE'] is not None:
        override = current_app.config['ARA_PLAYBOOK_OVERRIDE']
        files = files.filter(models.File.playbook_id.in_(override))
        facts = (facts
                 .join(models.Host)
                 .filter(models.Host.playbook_id.in_(override)))
        hosts = hosts.filter(models.Host.playbook_id.in_(override))
        playbooks = playbooks.filter(models.Playbook.id.in_(override))
        records = records.filter(models.Data.playbook_id.in_(override))
        tasks = tasks.filter(models.Task.playbook_id.in_(override))
        results = (results
                   .join(models.Task)
                   .filter(models.Task.playbook_id.in_(override)))

    return render_template(
        'about.html',
        active='about',
        files=fast_count(files),
        hosts=fast_count(hosts),
        facts=fast_count(facts),
        playbooks=fast_count(playbooks),
        records=fast_count(records),
        tasks=fast_count(tasks),
        results=fast_count(results)
    )
