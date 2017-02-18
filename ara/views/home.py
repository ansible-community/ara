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

from flask import render_template, Blueprint, current_app
from ara import models, utils

home = Blueprint('home', __name__)


@home.route('/')
def main():
    """ Returns the dashboard """
    if current_app.config['ARA_PLAYBOOK_OVERRIDE'] is not None:
        override = current_app.config['ARA_PLAYBOOK_OVERRIDE']
        playbooks = (models.Playbook.query
                     .filter(models.Playbook.id.in_(override))
                     .order_by(models.Playbook.time_start.desc()))
    else:
        playbooks = (models.Playbook.query
                     .order_by(models.Playbook.time_start.desc())
                     .limit(10))

    stats = utils.get_summary_stats(playbooks, 'playbook_id')

    return render_template('home.html', playbooks=playbooks, stats=stats)
