#  Copyright (c) 2018 Red Hat, Inc.
#
#  This file is part of ARA Records Ansible.
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

import cgi

from flask import Blueprint
from flask import Response
from flask import url_for

debug = Blueprint('debug', __name__)


@debug.record
def record_app(state):
    global app
    app = state.app


@debug.route('/config')
def config_dump():
    return '\n'.join(['<table>'] +
                     ['<tr><td>%s</td><td>%s</td></tr>' % (k, v)
                      for k, v in sorted(app.config.items())] +
                     ['</table>'])


@debug.route('/app')
def app_dump():
    lines = ['<table>']

    for attr in sorted(dir(app)):
        attrval = getattr(app, attr)
        lines.append('<tr>')
        lines.append('<td><a href="{url}">{attr}</a></td>'.format(
            url=url_for('debug.app_dump_attr', attr=attr),
            attr=attr))
        lines.append('<td>{_type}</td>'.format(
            _type=cgi.escape(str(type(attrval)))))
        lines.append('<td>{callable}</td>'.format(
            callable=callable(attrval)))
        lines.append('</tr>')

    lines.append('</table>')
    return '\n'.join(lines)


@debug.route('/app/<attr>')
def app_dump_attr(attr):
    return Response(repr(getattr(app, attr, None)),
                    mimetype='text/plain')


@debug.route('/map')
def map_dump():
    lines = ['<table>']

    for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
        lines.append('<tr>')
        lines.append(''.join('<td>%s</td>' % cgi.escape(col) for col in [
            rule.rule,
            ' '.join(rule.methods),
            rule.endpoint]))
        lines.append('</tr>')
    lines.append('</table>')
    return '\n'.join(lines)
