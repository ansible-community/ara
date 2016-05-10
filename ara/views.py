#   Copyright 2016 Red Hat, Inc. All Rights Reserved.
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

from flask import render_template
from ara import app, models, utils


# Routes
@app.route('/')
def main():
    """ Returns the home page """
    default_data = utils.default_data()
    return render_template('home.html', **default_data)


@app.route('/host/<host>')
@app.route('/host/<host>/<status>')
def host(host, status=None):
    default_data = utils.default_data()

    if status is not None:
        status_query = utils.status_to_query(status)
        data = models.Tasks.query.filter_by(host=host, **status_query)
    else:
        data = models.Tasks.query.filter_by(host=host)

    return render_template('host.html', host=host, data=data, **default_data)


@app.route('/task/<task>')
@app.route('/task/<task>/<status>')
def task(task, status=None):
    default_data = utils.default_data()

    task_name = models.Tasks.query.filter_by(id=task).first().task
    if status is not None:
        status_query = utils.status_to_query(status)
        data = models.Tasks.query.filter_by(task=task_name, **status_query)
    else:
        data = models.Tasks.query.filter_by(task=task_name)

    return render_template('task.html', task_name=task_name, task=task,
                           data=data, **default_data)


@app.route('/playbook/<playbook>')
@app.route('/playbook/<playbook>/<status>')
def playbook(playbook, status=None):
    default_data = utils.default_data()
    playbook_data = models.Playbooks.query.filter_by(playbook=playbook)
    playbook_name = playbook_data.first().playbook
    playbook_uuids = [playbook.id for playbook in playbook_data]

    if status is not None:
        status_query = utils.status_to_query(status)
        task_data = utils.get_tasks_for_playbooks(playbook_uuids,
                                                  **status_query)
    else:
        task_data = utils.get_tasks_for_playbooks(playbook_uuids)
    stats_data = utils.get_stats_for_playbooks(playbook_uuids)

    return render_template('playbook.html', playbook=playbook_name,
                           playbook_data=playbook_data, task_data=task_data,
                           stats_data=stats_data, **default_data)


@app.route('/run/<id>')
@app.route('/run/<id>/<status>')
def run(id, status=None):
    default_data = utils.default_data()
    playbook_data = models.Playbooks.query.filter_by(id=id).first()
    playbook = playbook_data.playbook

    if status is not None:
        status_query = utils.status_to_query(status)
        task_data = models.Tasks.query.filter_by(playbook_uuid=id,
                                                 **status_query)
    else:
        task_data = models.Tasks.query.filter_by(playbook_uuid=id)
    stats_data = models.Stats.query.filter_by(playbook_uuid=id)

    return render_template('run.html', playbook=playbook, id=id,
                           playbook_data=playbook_data, task_data=task_data,
                           stats_data=stats_data, **default_data)
