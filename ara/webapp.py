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

import logging
import logging.config
import os
import yaml

# Note (dmsimard): ARA's configuration, views and API imports are done
# "just-in-time" because we might end up loading them for nothing and it has a
# non-negligible cost.
# It also breaks some assumptions... For example, "ara.config" loads the
# configuration automatically on import which might not be desirable.

from ara.context_processors import configure_context_processors
from ara.db.models import db
from ara.errorhandlers import configure_errorhandlers
from ara.filters import configure_template_filters
from flask import abort
from flask import current_app
from flask import Flask
from flask import logging as flask_logging
from flask import send_from_directory

DEFAULT_APP_NAME = 'ara'


def create_app(config=None, app_name=None):
    if app_name is None:
        app_name = DEFAULT_APP_NAME

    if current_app:
        return current_app

    app = Flask(app_name)

    configure_app(app, config)
    configure_dirs(app)
    configure_logging(app)
    configure_errorhandlers(app)
    configure_template_filters(app)
    configure_context_processors(app)
    configure_blueprints(app)
    configure_api(app)
    configure_static_route(app)
    configure_db(app)
    configure_cache(app)

    return app


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


def configure_blueprints(app):
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

    if app.config.get('ARA_ENABLE_DEBUG_VIEW'):
        app.register_blueprint(ara.views.debug, url_prefix='/debug')


def configure_app(app, config):
    import ara.config  # flake8: noqa
    app.config.from_object(ara.config)

    if config is not None:
        app.config.from_object(config)

    app.config.from_envvar('ARA_CONFIG', silent=True)


def configure_dirs(app):
    if not os.path.isdir(app.config['ARA_DIR']):
        os.makedirs(app.config['ARA_DIR'], mode=0o700)


def configure_db(app):
    db.init_app(app)

    if app.config.get('ARA_AUTOCREATE_DATABASE'):
        with app.app_context():
            db.create_all()


def configure_logging(app):
    if app.config['ARA_LOG_CONFIG'] and os.path.exists(
            app.config['ARA_LOG_CONFIG']):
        config_path = app.config['ARA_LOG_CONFIG']
        if os.path.splitext(config_path)[1] in ('.yml', '.yaml', '.json'):
            # yaml.safe_load can load json as well as yaml
            logging.config.dictConfig(yaml.safe_load(open(config_path, 'r')))
        else:
            logging.config.fileConfig(config_path)
    elif app.config['ARA_LOG_FILE']:
        handler = logging.FileHandler(app.config['ARA_LOG_FILE'])
        # Set the ARA log format or fall back to the flask debugging format
        handler.setFormatter(
            logging.Formatter(app.config.get(
                'ARA_LOG_FORMAT', flask_logging.DEBUG_LOG_FORMAT)))
        logger = logging.getLogger(app.logger_name)
        logger.setLevel(app.config['ARA_LOG_LEVEL'])
        del logger.handlers[:]
        logger.addHandler(handler)

        for name in ('alembic', 'sqlalchemy.engine'):
            other_logger = logging.getLogger(name)
            other_logger.setLevel(logging.WARNING)
            del other_logger.handlers[:]
            other_logger.addHandler(handler)


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

    @app.route('/static/packaged/<module>/<path:filename>')
    def serve_static_packaged(module, filename):
        xstatic = current_app.config['XSTATIC']

        if module in xstatic:
            return send_from_directory(xstatic[module], filename)
        else:
            abort(404)


def configure_cache(app):
    """ Sets up an attribute to cache data in the app context """
    if not getattr(app, '_cache', None):
        app._cache = {}
