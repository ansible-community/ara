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

from flask import render_template, Blueprint, current_app
from ara import models

home = Blueprint('home', __name__)


@home.route('/')
def main():
    """ Returns the home page """
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

    return render_template('home.html',
                           active='home',
                           files=files.count(),
                           host_facts=host_facts.count(),
                           hosts=hosts.count(),
                           playbooks=playbooks.count(),
                           records=records.count(),
                           tasks=tasks.count(),
                           task_results=task_results.count())
