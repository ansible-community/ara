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

from flask import abort
from flask import Blueprint
from flask import current_app
from flask import send_from_directory

static = Blueprint('static', __name__)


@static.route('/packaged/<module>/<path:file>')
def serve(module, file):
    # Note (dmsimard)
    # /static/ is provided from in-tree bundled files and libraries.
    # /static/packaged/ is routed to serve packaged (i.e, XStatic) libraries.
    xstatic = current_app.config['XSTATIC']

    if module in xstatic:
        return send_from_directory(xstatic[module], file)
    else:
        abort(404)
