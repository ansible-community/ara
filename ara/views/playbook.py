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

from flask import render_template, Blueprint

playbook = Blueprint('playbook', __name__)


@playbook.route('/')
@playbook.route('/<playbook>/')
@playbook.route('/<playbook>/file/<file_>/')
@playbook.route('/<playbook>/results/')
@playbook.route('/<playbook>/host/<host>/')
@playbook.route('/<playbook>/host/<host>/<status>/')
@playbook.route('/<playbook>/play/<play>/')
@playbook.route('/<playbook>/task/<task>/')
def playbook_summary(playbook=None, file_=None, host=None, status=None,
                     play=None, task=None):

    return render_template('playbook_list.html')
