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

import datetime
import json

from ara import app, models


# Jinja filters
@app.template_filter('datetime')
def jinja_date_formatter(timestamp, format='%Y-%m-%d-%H:%M:%S.%f'):
    """ Reformats a datetime timestamp from str(datetime.datetime)"""
    datetime_format = "%Y-%m-%d %H:%M:%S.%f"
    timestamp = datetime.datetime.strptime(timestamp, datetime_format)
    return timestamp.strftime(format)[:-3]


@app.template_filter('truncate')
def jinja_truncate_string(string, length=40):
    """ Truncates a string to max length """
    return string[:length]


@app.template_filter('to_nice_json')
def jinja_to_nice_json(result):
    """ Formats a result """
    result = json.loads(result)
    return json.dumps(result, indent=4, sort_keys=True)


@app.template_filter('pick_status')
def jinja_pick_status(row):
    """ Returns the status of a row """
    if row.changed:
        return 'CHANGED'
    if row.skipped:
        return 'SKIPPED'
    if row.failed:
        return 'FAILED'
    return 'OK'


def default_data():
    data = {
        'hosts': [],
        'tasks': [],
        'plays': [],
        'playbooks': []
    }

    task_data = models.Tasks.query.all()
    for row in task_data:
        if row.host not in data['hosts']:
            data['hosts'].append(row.host)
        if row.task not in data['tasks']:
            data['tasks'].append(row.task)
        if row.play not in data['plays']:
            data['plays'].append(row.play)

    playbook_data = models.Playbooks.query.all()
    for row in playbook_data:
        if row.playbook not in data['playbooks']:
            data['playbooks'].append(row.playbook)

    return data
