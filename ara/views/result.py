from flask import render_template, abort, Blueprint
from ara import models

result = Blueprint('result', __name__)


@result.route('/<task_result>/')
def show_result(task_result):
    task_result = models.TaskResult.query.get(task_result)
    if task_result is None:
        abort(404)
    return render_template('task_result.html', task_result=task_result)
