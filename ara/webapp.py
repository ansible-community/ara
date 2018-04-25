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

# Note (dmsimard): ARA's configuration, views and API imports are done
# "just-in-time" because we might end up loading them for nothing and it has a
# non-negligible cost.
# It also breaks some assumptions... For example, "ara.config" loads the
# configuration automatically on import which might not be desirable.

import datetime
import flask_migrate
import logging
import logging.config
import os
import six
import sys

from ansible import __version__ as ansible_version
from ara import __release__ as ara_release
from ara.config.base import BaseConfig
from ara.config.logger import LogConfig
from ara.config.logger import setup_logging
from ara.config.webapp import WebAppConfig
from ara import models
from ara.utils import fast_count
from ara.utils import playbook_treeview

from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy.engine.reflection import Inspector

from flask import abort
from flask import Flask
from flask import render_template
from flask import send_from_directory
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
    configure_logging(app)
    configure_app_root(app)
    configure_blueprints(app)
    configure_static_route(app)
    configure_db(app)
    configure_errorhandlers(app)
    configure_template_filters(app)
    configure_context_processors(app)
    configure_cache(app)

    return app


def configure_app(app):
    app.config.update(BaseConfig().config)
    app.config.update(LogConfig().config)
    app.config.update(WebAppConfig().config)


def configure_dirs(app):
    if not os.path.isdir(app.config['ARA_DIR']):
        os.makedirs(app.config['ARA_DIR'], mode=0o700)


def configure_logging(app):
    setup_logging(app.config)


def configure_app_root(app):
    log = logging.getLogger('ara.webapp.configure_app_root')
    # Don't load the middleware needlessly if the root is actually '/'
    if app.config['APPLICATION_ROOT'] != '/':
        app.wsgi_app = AppRootMiddleware(app, app.wsgi_app)
    log.debug('Application root loaded: %s' % app.config['APPLICATION_ROOT'])


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
    log = logging.getLogger('ara.webapp.context_processors')
    log.debug('Loading context_processors...')

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
    log = logging.getLogger('ara.webapp.configure_blueprints')
    log.debug('Loading blueprints...')

    import ara.views  # flake8: noqa
    views = (
        (ara.views.about, '/about'),
        (ara.views.file, '/file'),
        (ara.views.host, '/host'),
        (ara.views.reports, ''),
        (ara.views.result, '/result'),
    )

    for view, prefix in views:
        app.register_blueprint(view, url_prefix=prefix)

    if app.config.get('ARA_LOG_LEVEL') == 'DEBUG':
        app.register_blueprint(ara.views.debug, url_prefix='/debug')


def configure_db(app):
    """
    0.10 is the first version of ARA that ships with a stable database schema.
    We can identify a database that originates from before this by checking if
    there is an alembic revision available.
    If there is no alembic revision available, assume we are running the first
    revision which contains the latest state of the database prior to this.
    """
    models.db.init_app(app)
    log = logging.getLogger('ara.webapp.configure_db')
    log.debug('Setting up database...')

    if app.config.get('ARA_AUTOCREATE_DATABASE'):
        with app.app_context():
            migrations = app.config['DB_MIGRATIONS']
            flask_migrate.Migrate(app, models.db, directory=migrations)
            config = app.extensions['migrate'].migrate.get_config(migrations)

            # Verify if the database tables have been created at all
            inspector = Inspector.from_engine(models.db.engine)
            if len(inspector.get_table_names()) == 0:
                log.info('Initializing new DB from scratch')
                flask_migrate.upgrade(directory=migrations)

            # Get current alembic head revision
            script = ScriptDirectory.from_config(config)
            head = script.get_current_head()

            # Get current revision, if available
            connection = models.db.engine.connect()
            context = MigrationContext.configure(connection)
            current = context.get_current_revision()

            if not current:
                log.info('Unstable DB schema, stamping original revision')
                flask_migrate.stamp(directory=migrations,
                                    revision='da9459a1f71c')

            if head != current:
                log.info('DB schema out of date, upgrading')
                flask_migrate.upgrade(directory=migrations)


def configure_static_route(app):
    # Note (dmsimard)
    # /static/ is provided from in-tree bundled files and libraries.
    # /static/packaged/ is routed to serve packaged (i.e, XStatic) libraries.
    #
    # The reason why this isn't defined as a proper view by itself is due to
    # a limitation in flask-frozen. Blueprint'd views methods are like so:
    # "<view>.<method>. The URL generator of flask-frozen is a method decorator
    # that expects the method name as the function and, obviously, you can't
    # really have dots in functions.
    # By having the route configured at the root of the application, there's no
    # dots and we can decorate "serve_static_packaged" instead of, say,
    # "static.serve_packaged".

    log = logging.getLogger('ara.webapp.configure_static_route')
    log.debug('Loading static routes...')

    @app.route('/static/packaged/<module>/<path:filename>')
    def serve_static_packaged(module, filename):
        xstatic = app.config['XSTATIC']

        if module in xstatic:
            return send_from_directory(xstatic[module], filename)
        else:
            abort(404)


def configure_cache(app):
    """ Sets up an attribute to cache data in the app context """
    log = logging.getLogger('ara.webapp.configure_cache')
    log.debug('Configuring cache')

    if not getattr(app, '_cache', None):
        app._cache = {}


class AppRootMiddleware(object):
    """
    Middleware to manage route prefixes, for example when hosting ARA in a
    subdirectory.
    """
    def __init__(self, app, wsgi_app):
        self.log = logging.getLogger('ara.webapp.AppRootMiddleware')
        self.log.debug('Initializing AppRootMiddleware')
        self.app = app
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        root = self.app.config['APPLICATION_ROOT']
        if environ['PATH_INFO'].startswith(root):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(root):]
            environ['SCRIPT_NAME'] = root
            self.log.debug('Returning with root %s' % root)
            return self.wsgi_app(environ, start_response)
        else:
            self.log.debug('Returning 404 for %s' % environ['PATH_INFO'])
            url = "{scheme}://{host}{root}".format(
                scheme=environ['wsgi.url_scheme'],
                host=environ['HTTP_HOST'],
                root=root,
            )
            msg = """
            This URL doesn't belong to an ARA application. <br />
            <br />
            Did you mean to browse to <a href='{url}'>{url}</a> instead ?
            """.format(url=url)
            start_response('404', [('Content-Type', 'text/html')])
            return [msg.strip().encode()]
