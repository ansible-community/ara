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

import json
import six

from flask import render_template, abort, Blueprint, current_app
from ara import models

host = Blueprint('host', __name__)


@host.route('/')
def index():
    """
    This is not served anywhere in the web application.
    It is used explicitly in the context of generating static files since
    flask-frozen requires url_for's to crawl content.
    url_for's are not used with host.show_host directly and are instead
    dynamically generated through javascript for performance purposes.
    """
    if current_app.config['ARA_PLAYBOOK_OVERRIDE'] is not None:
        override = current_app.config['ARA_PLAYBOOK_OVERRIDE']
        hosts = (models.Host.query
                 .filter(models.Host.playbook_id.in_(override)))
    else:
        hosts = models.Host.query.all()

    return render_template('host_index.html', hosts=hosts)


@host.route('/<id>/')
def show_host(id):
    try:
        host = models.Host.query.get(id)
    except models.NoResultFound:
        abort(404)

    if host and host.facts:
        facts = sorted(six.iteritems(json.loads(host.facts.values)))
    else:
        abort(404)

    return render_template('host.html',
                           host=host,
                           facts=facts)
