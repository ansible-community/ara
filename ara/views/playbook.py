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

from flask import render_template, abort, Blueprint, request
from ara import models, utils

playbook = Blueprint('playbook', __name__)


@playbook.route('/')
def playbook_summary():
    playbooks = (models.Playbook.query
                 .order_by(models.Playbook.time_start.desc()))
    stats = utils.get_summary_stats(playbooks, 'playbook_id')

    return render_template('playbook_list.html',
                           playbooks=playbooks,
                           stats=stats)


@playbook.route('/<playbook>/')
@playbook.route('/<playbook>/file/<file_>/')
def show_playbook(playbook, file_=None):
    playbook = models.Playbook.query.get(playbook)
    if playbook is None:
        abort(404)

    plays = (models.Play.query
             .filter(models.Play.playbook_id == playbook.id)
             .order_by(models.Play.sortkey))

    playbook_file = (models.File.query
                     .filter(models.File.playbook_id == playbook.id)
                     .filter(models.File.is_playbook.is_(True))).one()

    files = (models.File.query
             .filter(models.File.playbook_id == playbook.id)
             .filter(models.File.is_playbook.is_(False))
             .order_by(models.File.path))

    tasks = (models.Task.query
             .filter(models.Task.playbook_id == playbook.id)
             .order_by(models.Task.sortkey))

    try:
        data = (models.Data.query
                .filter(models.Data.playbook_id == playbook.id)
                .order_by(models.Data.key))
        # If there are no results, don't return an empty query
        if not data.count():
            data = None
    except models.NoResultFound:
        data = None

    if file_:
        file_ = (models.File.query.get(file_))
        if file_ is None:
            abort(404)

        tasks = (tasks
                 .join(models.File)
                 .filter(models.File.id == file_.id))

    return render_template('playbook.html',
                           playbook=playbook,
                           plays=plays,
                           playbook_file=playbook_file,
                           files=files,
                           tasks=tasks,
                           data=data,
                           file_=file_)


@playbook.route('/<playbook>/results/')
@playbook.route('/<playbook>/host/<host>/')
@playbook.route('/<playbook>/host/<host>/<status>/')
@playbook.route('/<playbook>/play/<play>/')
@playbook.route('/<playbook>/task/<task>/')
def playbook_results(playbook, host=None, play=None, task=None, status=None):
    playbook = models.Playbook.query.get(playbook)
    if playbook is None:
        abort(404)

    task_results = (models.TaskResult.query
                    .join(models.Task)
                    .join(models.Play)
                    .join(models.Host)
                    .join(models.Playbook)
                    .filter(models.Playbook.id == playbook.id)
                    .order_by(models.TaskResult.time_start))

    hosts = None
    host = host or request.args.get('host')
    if host is not None:
        hosts = [str(h) for h in host.split(',')]
        task_results = (task_results
                        .filter(models.Host.name.in_(hosts)))

    plays = None
    play = play or request.args.get('play')
    if play is not None:
        plays = [str(h) for h in play.split(',')]
        task_results = (task_results
                        .filter(models.Play.id.in_(plays)))

    playbook_file = (models.File.query
                     .filter(models.File.playbook_id == playbook.id)
                     .filter(models.File.is_playbook.is_(True))).one()

    files = (models.File.query
             .filter(models.File.playbook_id == playbook.id)
             .filter(models.File.is_playbook.is_(False))
             .order_by(models.File.path))

    task = task or request.args.get('task')
    if task is not None:
        tasks = [str(h) for h in task.split(',')]
        task_results = (task_results
                        .filter(models.Task.id.in_(tasks)))

    try:
        data = (models.Data.query
                .filter(models.Data.playbook_id == playbook.id)
                .order_by(models.Data.key))
        # If there are no results, don't return an empty query
        if not data.count():
            data = None
    except models.NoResultFound:
        data = None

    # LKS: We're filtering this with Python rather than SQL.  This
    # may become relevant if we implement result paging.
    status = status or request.args.get('status')
    if status is not None:
        status = status.split(',')
        task_results = (res for res in task_results
                        if res.derived_status in status)

    return render_template('playbook_results.html',
                           hosts=hosts,
                           plays=plays,
                           files=files,
                           data=data,
                           playbook=playbook,
                           playbook_file=playbook_file,
                           task_results=task_results)
