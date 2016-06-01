from flask import render_template, abort, Blueprint, request
from ara import models

task = Blueprint('task', __name__)


@task.route('/<task>/')
def show_task(task):
    task = models.Task.query.get(task)
    if task is None:
        abort(404)

    task_results = (models.TaskResult.query
                    .join(models.Task)
                    .join(models.Host)
                    .join(models.Playbook)
                    .filter(models.Task.id == task.id)
                    .order_by(models.TaskResult.time_start))

    if request.args.get('host'):
        hosts = [str(host) for host in request.args.get('host').split(',')]
        task_results = (task_results
                        .filter(models.Host.name.in_(hosts)))

    if request.args.get('status'):
        status = request.args.get('status').split(',')
        task_results = (res for res in task_results
                        if res.derived_status in status)

    return render_template('task.html',
                           playbook=task.playbook,
                           task=task,
                           task_results=task_results)
