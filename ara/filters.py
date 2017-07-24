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

import datetime
import logging
import six

from ara.utils import fast_count
from ara.utils import playbook_treeview
from jinja2 import Markup
from os import path
from oslo_serialization import jsonutils
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import YamlLexer
from pygments.lexers import JsonLexer
from pygments.lexers.special import TextLexer


def configure_template_filters(app):
    log = logging.getLogger('%s.filters' % app.logger_name)

    @app.template_filter('datefmt')
    def jinja_date_formatter(timestamp, format='%Y-%m-%d %H:%M:%S'):
        """ Reformats a datetime timestamp from str(datetime.datetime) """
        if timestamp is None:
            return 'n/a'
        else:
            return datetime.datetime.strftime(timestamp, format)

    @app.template_filter('timefmt')
    def jinja_time_formatter(timestamp):
        """ Reformats a datetime timedelta """
        if timestamp is None:
            return 'n/a'
        else:
            date = datetime.timedelta(seconds=int(timestamp.total_seconds()))
            return str(date)

    @app.template_filter('to_nice_json')
    def jinja_to_nice_json(result):
        """ Tries to format a result as a pretty printed JSON. """
        try:
            return jsonutils.dumps(jsonutils.loads(result),
                                   indent=4,
                                   sort_keys=True)
        except (ValueError, TypeError):
            try:
                return jsonutils.dumps(result, indent=4, sort_keys=True)
            except TypeError as err:
                log.error('failed to dump json: %s', err)
                return result

    @app.template_filter('from_json')
    def jinja_from_json(val):
        try:
            return jsonutils.loads(val)
        except ValueError as err:
            log.error('failed to load json: %s', err)
            return val

    @app.template_filter('yamlhighlight')
    def jinja_yamlhighlight(code):
        formatter = HtmlFormatter(linenos='table',
                                  anchorlinenos=True,
                                  lineanchors='line',
                                  linespans='line',
                                  cssclass='codehilite')

        if not code:
            code = ''

        return highlight(Markup(code).unescape(),
                         YamlLexer(stripall=True),
                         formatter)

    @app.template_filter('pygments_formatter')
    def jinja_pygments_formatter(data):
        formatter = HtmlFormatter(cssclass='codehilite')

        if isinstance(data, dict) or isinstance(data, list):
            data = jsonutils.dumps(data, indent=4, sort_keys=True)
            lexer = JsonLexer()
        elif six.string_types or six.text_type:
            try:
                data = jsonutils.dumps(jsonutils.loads(data),
                                       indent=4,
                                       sort_keys=True)
                lexer = JsonLexer()
            except (ValueError, TypeError):
                lexer = TextLexer()
        else:
            lexer = TextLexer()

        lexer.stripall = True
        return highlight(Markup(data).unescape(), lexer, formatter)

    @app.template_filter('fast_count')
    def jinja_fast_count(query):
        return fast_count(query)

    @app.template_filter('basename')
    def jinja_basename(pathname):
        return path.basename(pathname)

    @app.template_filter('treeview')
    def jinja_treeview(playbook):
        return playbook_treeview(playbook)
