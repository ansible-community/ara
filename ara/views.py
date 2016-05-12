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

from flask import render_template, request
from ara import app, models, utils


# Routes
@app.route('/')
def main():
    """ Returns the home page """
    return render_template('home.html')


@app.route('/host/<host>')
def host(host):
    host = models.Host.query.filter_by(name=host).one()
    return render_template('host.html', host=host)


@app.route('/task/<task>')
def task(task):
    task = models.Task.query.get(task)
    return render_template('task.html', task=task)


@app.route('/taskresult/<taskresult>')
def taskresult(taskresult):
    pass


@app.route('/play/<play>')
def play(play):
    play = models.Play.query.get(play)
    return render_template('play.html', play=play)


@app.route('/playbook')
def playbook_summary():
    playbooks = models.Playbook.query.order_by(
        models.Playbook.time_start)

    return render_template('playbook_summary.html',
                           playbooks=playbooks)

@app.route('/playbook/<playbook>')
def playbook(playbook):
    playbook = models.Playbook.query.get(playbook)
    return render_template('playbook.html', playbook=playbook)


@app.route('/playbook/<playbook>/host/<host>')
def playbook_host(playbook, host):
    host = models.Host.query.filter_by(name=host).one()
    playbook = models.Playbook.query.get(playbook)
    task_results = (models.TaskResult.query
                    .join(models.Task)
                    .join(models.Host)
                    .join(models.Playbook)
                    .filter(models.Playbook.id == playbook.id)
                    .filter(models.Host.name == host.name))

    return render_template('playbook_host.html',
                           playbook=playbook,
                           host=host,
                           task_results=task_results)
