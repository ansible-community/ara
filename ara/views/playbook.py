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

    tasks = (models.Task.query
             .filter(models.Task.playbook_id == playbook.id)
             .order_by(models.Task.sortkey))

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
                           tasks=tasks,
                           file_=file_)


@playbook.route('/<playbook>/results/')
@playbook.route('/<playbook>/results/<host>/')
@playbook.route('/<playbook>/results/<host>/<status>/')
def playbook_results(playbook, host=None, status=None):
    playbook = models.Playbook.query.get(playbook)
    if playbook is None:
        abort(404)

    task_results = (models.TaskResult.query
                    .join(models.Task)
                    .join(models.Host)
                    .join(models.Playbook)
                    .filter(models.Playbook.id == playbook.id)
                    .order_by(models.TaskResult.time_start))

    host = host or request.args.get('host')
    if host is not None:
        hosts = [str(h) for h in host.split(',')]
        task_results = (task_results
                        .filter(models.Host.name.in_(hosts)))

    # LKS: We're filtering this with Python rather than SQL.  This
    # may become relevant if we implement result paging.
    status = status or request.args.get('status')
    if status is not None:
        status = status.split(',')
        task_results = (res for res in task_results
                        if res.derived_status in status)

    return render_template('playbook_results.html',
                           playbook=playbook,
                           task_results=task_results)
