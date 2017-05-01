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

import datetime
import json
import logging

from ara.utils import fast_count
from ara.utils import playbook_treeview
from jinja2 import Markup
from jinja2 import UndefinedError
from os import path
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import YamlLexer


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
            return json.dumps(json.loads(result), indent=4, sort_keys=True)
        except (ValueError, TypeError):
            try:
                return json.dumps(result, indent=4, sort_keys=True)
            except TypeError as err:
                log.error('failed to dump json: %s', err)
                return result

    @app.template_filter('from_json')
    def jinja_from_json(val):
        try:
            return json.loads(val)
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

        # We have little control over the content of the files we're
        # formatting. This can lead into UnicodeDecodeError raised by Jinja
        # due to breaking whitespace characters or other possibly encoded
        # characters.
        try:
            code = code.decode('utf-8')
        except UndefinedError:
            code = ''

        return highlight(Markup(code.rstrip()).unescape(),
                         YamlLexer(),
                         formatter)

    @app.template_filter('fast_count')
    def jinja_fast_count(query):
        return fast_count(query)

    @app.template_filter('basename')
    def jinja_basename(pathname):
        return path.basename(pathname)

    @app.template_filter('treeview')
    def jinja_treeview(playbook):
        return playbook_treeview(playbook)
