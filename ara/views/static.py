#  Copyright (c) 2017 Red Hat, Inc.
#
#  This file is part of ARA: Ansible Run Analysis.
#
#  ARA is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  ARA is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with ARA.  If not, see <http://www.gnu.org/licenses/>.

from flask import Blueprint
from flask import abort
from flask import current_app
from flask import send_from_directory

static = Blueprint('static', __name__)


@static.route('/packaged/<module>/<path:filename>')
def packaged(module, filename):
    xstatic = current_app.config['XSTATIC']

    if module in xstatic:
        return send_from_directory(xstatic[module], filename)
    else:
        abort(404)
