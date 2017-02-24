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

from flask import render_template, Blueprint, current_app, redirect, url_for
from ara import models, utils

reports = Blueprint('reports', __name__)


@reports.route('/')
@reports.route('/<int:page>')
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
