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

from flask import render_template, abort, Blueprint
from ara import models

result = Blueprint('result', __name__)


@result.route('/<task_result>/')
def show_result(task_result):
    task_result = models.TaskResult.query.get(task_result)
    if task_result is None:
        abort(404)
    return render_template('task_result.html', task_result=task_result)
