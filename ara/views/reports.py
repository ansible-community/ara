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

import logging

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
log = logging.getLogger(__name__)


# This is a flask-frozen workaround in order to generate an index.html
# at the root of the generated report.
@reports.route('/index.html')
def main():
    return redirect('/')


@reports.route('/')
@reports.route('/reports/')
@reports.route('/reports/list/<int:page>.html')
def report_list(page=1):
    if current_app.config['ARA_PLAYBOOK_OVERRIDE'] is not None:
        override = current_app.config['ARA_PLAYBOOK_OVERRIDE']
        playbooks = (models.Playbook.query
                     .filter(models.Playbook.id.in_(override))
                     .order_by(models.Playbook.time_start.desc()))
    else:
        playbooks = (models.Playbook.query
                     .order_by(models.Playbook.time_start.desc()))

    if not utils.fast_count(playbooks):
        return redirect(url_for('about.main'))

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


@reports.route('/reports/<playbook_id>.html')
def report(playbook_id):
    playbook = models.Playbook.query.get(playbook_id)
    if playbook is None:
        abort(404)

    stats = utils.get_summary_stats([playbook], 'playbook_id')

    result_per_page = current_app.config['ARA_RESULT_PER_PAGE']

    return render_template('report_single.html',
                           active='reports',
                           result_per_page=result_per_page,
                           playbook=playbook,
                           stats=stats)

# Note (dmsimard)
# We defer the loading of the different data tables and render them
# asynchronously for performance purposes.
# Because of this, we need to prepare some JSON data so data tables can
# retrieve it through AJAX:
#   https://datatables.net/examples/ajax/defer_render.html
# The following routes are there to support this mechanism.
# The routes have a text extension for proper mimetype detection.


@reports.route('/reports/ajax/parameters/<playbook>.txt')
def ajax_parameters(playbook):
    playbook = models.Playbook.query.get(playbook)
    if playbook is None:
        abort(404)

    results = dict()
    results['data'] = list()

    results['data'].append(['playbook_path', playbook.path])
    results['data'].append(['ansible_version', playbook.ansible_version])

    log.debug('Loading playbook parameters')
    if playbook.options:
        for option in playbook.options:
            results['data'].append([option, playbook.options[option]])

    log.debug('%s playbook parameters loaded' % len(results['data']))
    return jsonify(results)


@reports.route('/reports/ajax/plays/<playbook>.txt')
def ajax_plays(playbook):
    plays = (models.Play.query
             .filter(models.Play.playbook_id == playbook))
    if not utils.fast_count(plays):
        abort(404)

    jinja = current_app.jinja_env
    date = jinja.from_string('{{ date | datefmt }}')
    time = jinja.from_string('{{ time | timefmt }}')

    results = dict()
    results['data'] = list()

    log.debug('Loading plays')
    for play in plays:
        name = u"<span class='pull-left'>{0}</span>".format(play.name)
        start = date.render(date=play.time_start)
        end = date.render(date=play.time_end)
        duration = time.render(time=play.duration)
        results['data'].append([name, start, end, duration])

    log.debug('%s plays loaded' % len(results['data']))
    return jsonify(results)


@reports.route('/reports/ajax/records/<playbook>.txt')
def ajax_records(playbook):
    records = (models.Data.query
               .filter(models.Data.playbook_id == playbook))
    if not utils.fast_count(records):
        abort(404)

    jinja = current_app.jinja_env
    record_key = jinja.get_template('ajax/record_key.html')
    record_value = jinja.get_template('ajax/record_value.html')

    results = dict()
    results['data'] = list()

    log.debug('Loading records')
    for record in records:
        key = record_key.render(record=record)
        value = record_value.render(record=record)

        results['data'].append([key, value])

    log.debug('%s records loaded' % len(results['data']))
    return jsonify(results)


@reports.route('/reports/ajax/results/<playbook>.txt')
def ajax_results(playbook):
    tasks_in_playbook = models.Task.query.filter(
        models.Task.playbook_id == playbook)
    if not utils.fast_count(tasks_in_playbook):
        abort(404)

    jinja = current_app.jinja_env
    time = jinja.from_string('{{ time | timefmt }}')
    action_link = jinja.get_template('ajax/action.html')
    name_cell = jinja.get_template('ajax/task_name.html')
    task_status_link = jinja.get_template('ajax/task_status.html')

    results = dict()
    results['data'] = list()

    log.debug('Loading results')
    for task in tasks_in_playbook:
        task_results = task.task_results
        for result in task_results:
            name = name_cell.render(tags=result.task.tags,
                                    name=result.task.name)
            host = result.host.name
            action = action_link.render(file=result.task.file,
                                        lineno=result.task.lineno,
                                        action=result.task.action)
            elapsed = time.render(time=result.task.offset_from_playbook)
            duration = time.render(time=result.duration)
            status = task_status_link.render(
                id=result.id, derived_status=result.derived_status)
            results['data'].append([name, host, action,
                                    elapsed, duration, status])
        del task_results
        del task

    log.debug('%s results loaded' % len(results['data']))
    return jsonify(results)


@reports.route('/reports/ajax/stats/<playbook>.txt')
def ajax_stats(playbook):
    stats = (models.Stats.query
             .filter(models.Stats.playbook_id == playbook))
    if not utils.fast_count(stats):
        abort(404)

    jinja = current_app.jinja_env
    host_link = jinja.get_template('ajax/stats.html')

    results = dict()
    results['data'] = list()

    log.debug('Loading host statistics and facts')
    for stat in stats:
        host = host_link.render(host=stat.host)
        ok = stat.ok if stat.ok >= 1 else 0
        changed = stat.changed if stat.changed >= 1 else 0
        failed = stat.failed if stat.failed >= 1 else 0
        skipped = stat.skipped if stat.skipped >= 1 else 0
        unreachable = stat.unreachable if stat.unreachable >= 1 else 0

        data = [host, ok, changed, failed, skipped, unreachable]
        results['data'].append(data)

    log.debug('%s host stats and facts loaded' % len(results['data']))
    return jsonify(results)
