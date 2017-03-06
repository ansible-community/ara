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

from ara import models
from ara import utils
from flask import abort
from flask import Blueprint
from flask import current_app
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import url_for

reports = Blueprint('reports', __name__)


@reports.route('/')
@reports.route('/<int:page>.html')
def report_list(page=1):
    if current_app.config['ARA_PLAYBOOK_OVERRIDE'] is not None:
        override = current_app.config['ARA_PLAYBOOK_OVERRIDE']
        playbooks = (models.Playbook.query
                     .filter(models.Playbook.id.in_(override))
                     .order_by(models.Playbook.time_start.desc()))
    else:
        playbooks = (models.Playbook.query
                     .order_by(models.Playbook.time_start.desc()))

    if not playbooks.count():
        return redirect(url_for('home.main'))

    playbook_per_page = current_app.config['ARA_PLAYBOOK_PER_PAGE']
    # Paginate unless playbook_per_page is set to 0
    if playbook_per_page >= 1:
        playbooks = playbooks.paginate(page, playbook_per_page, False)
    else:
        playbooks = playbooks.paginate(page, None, False)

    stats = utils.get_summary_stats(playbooks.items, 'playbook_id')

    result_per_page = current_app.config['ARA_RESULT_PER_PAGE']

    return render_template('report_list.html',
                           active='reports',
                           result_per_page=result_per_page,
                           playbooks=playbooks,
                           stats=stats)

# Note (dmsimard)
# We defer the loading of the different data tables and render them
# asynchronously for performance purposes.
# Because of this, we need to prepare some JSON data so data tables can
# retrieve it through AJAX:
#   https://datatables.net/examples/ajax/defer_render.html
# The following routes are there to support this mechanism.
# The routes have a text extension for proper mimetype detection.


@reports.route('/ajax/files/<playbook>.txt')
def ajax_files(playbook):
    files = (models.File.query
             .filter(models.File.playbook_id.in_([playbook])))
    if not files.count():
        abort(404)

    jinja = current_app.jinja_env
    action_link = jinja.get_template('ajax/file.html')

    results = dict()
    results['data'] = list()

    for file in files:
        results['data'].append([action_link.render(file=file)])

    return jsonify(results)


@reports.route('/ajax/plays/<playbook>.txt')
def ajax_plays(playbook):
    plays = (models.Play.query
             .filter(models.Play.playbook_id.in_([playbook])))
    if not plays.count():
        abort(404)

    jinja = current_app.jinja_env
    date = jinja.from_string('{{ date | datefmt }}')
    time = jinja.from_string('{{ time | timefmt }}')

    results = dict()
    results['data'] = list()

    for play in plays:
        name = "<span class='pull-left'>{0}</span>".format(play.name)
        start = date.render(date=play.time_start)
        end = date.render(date=play.time_end)
        duration = time.render(time=play.duration)
        results['data'].append([name, start, end, duration])

    return jsonify(results)


@reports.route('/ajax/records/<playbook>.txt')
def ajax_records(playbook):
    records = (models.Data.query
               .filter(models.Data.playbook_id.in_([playbook])))
    if not records.count():
        abort(404)

    jinja = current_app.jinja_env
    record_key = jinja.get_template('ajax/record_key.html')
    record_value = jinja.get_template('ajax/record_value.html')

    results = dict()
    results['data'] = list()

    for record in records:
        key = record_key.render(record=record)
        value = record_value.render(record=record)

        results['data'].append([key, value])

    return jsonify(results)


@reports.route('/ajax/results/<playbook>.txt')
def ajax_results(playbook):
    task_results = (models.TaskResult.query
                    .join(models.Task)
                    .filter(models.Task.playbook_id.in_([playbook])))
    if not task_results.count():
        abort(404)

    jinja = current_app.jinja_env
    time = jinja.from_string('{{ time | timefmt }}')
    action_link = jinja.get_template('ajax/action.html')
    task_status_link = jinja.get_template('ajax/task_status.html')

    results = dict()
    results['data'] = list()

    for result in task_results:
        name = "<span class='pull-left'>{0}</span>".format(result.task.name)
        host = result.host.name
        action = action_link.render(result=result)
        elapsed = time.render(time=result.task.offset_from_playbook)
        duration = time.render(time=result.duration)
        status = task_status_link.render(result=result)

        results['data'].append([name, host, action, elapsed, duration, status])
    return jsonify(results)


@reports.route('/ajax/stats/<playbook>.txt')
def ajax_stats(playbook):
    stats = (models.Stats.query
             .filter(models.Stats.playbook_id.in_([playbook])))
    if not stats.count():
        abort(404)

    jinja = current_app.jinja_env
    host_link = jinja.get_template('ajax/stats.html')

    results = dict()
    results['data'] = list()

    for stat in stats:
        host = host_link.render(stat=stat)
        ok = stat.ok if stat.ok >= 1 else 0
        changed = stat.changed if stat.changed >= 1 else 0
        failed = stat.failed if stat.failed >= 1 else 0
        skipped = stat.skipped if stat.skipped >= 1 else 0
        unreachable = stat.unreachable if stat.unreachable >= 1 else 0

        data = [host, ok, changed, failed, skipped, unreachable]
        results['data'].append(data)

    return jsonify(results)
