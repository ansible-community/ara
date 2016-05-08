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
def host(host):
    default_data = utils.default_data()
    data = models.Tasks.query.filter_by(host=host)

    return render_template('host.html', host=host, data=data, **default_data)


@app.route('/task/<task>')
def task(task):
    default_data = utils.default_data()
    data = models.Tasks.query.filter_by(task=task)

    return render_template('task.html', task=task, data=data, **default_data)


@app.route('/play/<play>')
def play(play):
    default_data = utils.default_data()
    data = models.Tasks.query.filter_by(play=play)

    return render_template('play.html', play=play, data=data, **default_data)


@app.route('/playbook/<playbook>')
def playbook(playbook):
    default_data = utils.default_data()
    playbook_data = models.Playbooks.query.filter_by(playbook=playbook).first()
    playbook_uuid = playbook_data.id

    task_data = models.Tasks.query.filter_by(playbook_uuid=playbook_uuid)
    stats_data = models.Stats.query.filter_by(playbook_uuid=playbook_uuid)

    return render_template('playbook.html', playbook=playbook,
                           playbook_data=playbook_data, task_data=task_data,
                           stats_data=stats_data, **default_data)
