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

# Note (dmsimard): ARA's configuration, views and API imports are done
# "just-in-time" because we might end up loading them for nothing and it has a
# non-negligible cost.
# It also breaks some assumptions... For example, "ara.config" loads the
# configuration automatically on import which might not be desirable.

import datetime
import logging
import logging.config
import os
import six
import sys

from ansible import __version__ as ansible_version
from ara import __release__ as ara_release
from ara.db import models
from ara.db.models import db
from ara.utils import fast_count
from ara.utils import playbook_treeview

from flask import Flask
from flask import render_template
from jinja2 import Markup
from oslo_serialization import jsonutils
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import YamlLexer
from pygments.lexers import JsonLexer
from pygments.lexers.special import TextLexer


def create_app():
    app = Flask('ara')

    configure_app(app)
    configure_dirs(app)
    configure_logging()
    configure_errorhandlers(app)
    configure_template_filters(app)
    configure_context_processors(app)
    configure_blueprints(app)
    configure_api(app)
    configure_db(app)
    configure_cache(app)

    return app


def configure_app(app):
    app.config.from_object('ara.config.base')
    app.config.from_object('ara.config.logger')
    app.config.from_object('ara.config.webapp')


def configure_dirs(app):
    if not os.path.isdir(app.config['ARA_DIR']):
        os.makedirs(app.config['ARA_DIR'], mode=0o700)


def configure_logging():
    from ara.config.logger import setup_logging
    setup_logging()


def configure_errorhandlers(app):
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html', error=error), 404


def configure_template_filters(app):
    log = logging.getLogger('ara.filters')

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

    # TODO: Remove fast_count, replace by "select id, order desc, limit 1"
    @app.template_filter('fast_count')
    def jinja_fast_count(query):
        return fast_count(query)

    @app.template_filter('basename')
    def jinja_basename(pathname):
        return os.path.basename(pathname)

    @app.template_filter('treeview')
    def jinja_treeview(playbook):
        return playbook_treeview(playbook)


def configure_context_processors(app):
    @app.context_processor
    def ctx_add_nav_data():
        """
        Returns standard data that will be available in every template view.
        """
        try:
            models.Playbook.query.one()
            empty_database = False
        except models.MultipleResultsFound:
            empty_database = False
        except models.NoResultFound:
            empty_database = True

        # Get python version info
        major, minor, micro, release, serial = sys.version_info

        return dict(ara_version=ara_release,
                    ansible_version=ansible_version,
                    python_version="{0}.{1}".format(major, minor),
                    empty_database=empty_database)


def configure_blueprints(app):
    import ara.views  # flake8: noqa
    views = (
        (ara.views.about, '/about'),
        (ara.views.file, '/file'),
        (ara.views.host, '/host'),
        (ara.views.reports, ''),
        (ara.views.result, '/result'),
        (ara.views.static, '/static')
    )

    for view, prefix in views:
        app.register_blueprint(view, url_prefix=prefix)

    if app.config.get('ARA_ENABLE_DEBUG_VIEW'):
        app.register_blueprint(ara.views.debug, url_prefix='/debug')


def configure_api(app):
    import ara.api.v1.hosts  # flake8: noqa
    import ara.api.v1.files  # flake8: noqa
    import ara.api.v1.playbooks  # flake8: noqa
    import ara.api.v1.plays  # flake8: noqa
    import ara.api.v1.records  # flake8: noqa
    import ara.api.v1.results  # flake8: noqa
    import ara.api.v1.tasks  # flake8: noqa

    endpoints = (
        (ara.api.v1.hosts.blueprint, '/api/v1/hosts'),
        (ara.api.v1.files.blueprint, '/api/v1/files'),
        (ara.api.v1.playbooks.blueprint, '/api/v1/playbooks'),
        (ara.api.v1.plays.blueprint, '/api/v1/plays'),
        (ara.api.v1.records.blueprint, '/api/v1/records'),
        (ara.api.v1.results.blueprint, '/api/v1/results'),
        (ara.api.v1.tasks.blueprint, '/api/v1/tasks'),
    )
    for endpoint, prefix in endpoints:
        app.register_blueprint(endpoint, url_prefix=prefix)


def configure_db(app):
    db.init_app(app)

    if app.config.get('ARA_AUTOCREATE_DATABASE'):
        with app.app_context():
            db.create_all()


def configure_cache(app):
    """ Sets up an attribute to cache data in the app context """
    if not getattr(app, '_cache', None):
        app._cache = {}
