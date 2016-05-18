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


@app.route('/')
def main():
    """ Returns the home page """
    return render_template('home.html')


@app.route('/host')
def host_summary():
    hosts = models.Host.query.order_by(models.Host.name)
    stats = utils.get_summary_stats(hosts, 'host_id')

    return render_template('host_summary.html',
                           hosts=hosts,
                           stats=stats)


@app.route('/host/<host>')
def host(host):
    host = models.Host.query.filter_by(name=host).one()
    return render_template('host.html', host=host)


@app.route('/task/<task>')
def task(task):
    task = models.Task.query.get(task)
    return render_template('task.html', task=task)


@app.route('/task_result/<task_result>')
def task_result(task_result):
    task_result = models.TaskResult.query.get(task_result)
    return render_template('task_result.html', task_result=task_result)


@app.route('/play/<play>')
def play(play):
    play = models.Play.query.get(play)
    return render_template('play.html', play=play)


@app.route('/playbook')
def playbook_summary():
    playbooks = models.Playbook.query.order_by(models.Playbook.time_start)
    stats = utils.get_summary_stats(playbooks, 'playbook_id')

    return render_template('playbook_summary.html',
                           playbooks=playbooks,
                           stats=stats)


@app.route('/playbook/<playbook>')
def playbook(playbook):
    playbook = models.Playbook.query.get(playbook)
    return render_template('playbook.html', playbook=playbook)


@app.route('/playbook/<playbook>/host/<host>')
@app.route('/playbook/<playbook>/host/<host>/status/<status>')
def playbook_host(playbook, host, status=None):
    host = models.Host.query.filter_by(name=host).one()
    playbook = models.Playbook.query.get(playbook)

    task_results = models.TaskResult.query

    if status is not None:
        status_query = utils.status_to_query(status)
        task_results = task_results.filter_by(**status_query)

    task_results = (task_results
                    .join(models.Task)
                    .join(models.Host)
                    .join(models.Playbook)
                    .filter(models.Playbook.id == playbook.id)
                    .filter(models.Host.name == host.name)
                    .order_by(models.TaskResult.time_start))

    return render_template('playbook_host.html',
                           playbook=playbook,
                           host=host,
                           task_results=task_results,
                           status=status)
