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

import os
import logging
import flask_migrate

from alembic.script import ScriptDirectory
from alembic.migration import MigrationContext
from flask import Flask, current_app
from flask import logging as flask_logging
from sqlalchemy.engine.reflection import Inspector

from ara.models import db
from ara.filters import configure_template_filters
from ara.context_processors import configure_context_processors
from ara.errorhandlers import configure_errorhandlers
import ara.views
import ara.config


DEFAULT_APP_NAME = 'ara'

views = (
    (ara.views.file, '/file'),
    (ara.views.home, ''),
    (ara.views.host, '/host'),
    (ara.views.playbook, '/playbook'),
    (ara.views.reports, '/reports'),
    (ara.views.result, '/result'),
)


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
    configure_db(app)

    return app


def configure_blueprints(app):
    for view, prefix in views:
        app.register_blueprint(view, url_prefix=prefix)

    if app.config.get('ARA_ENABLE_DEBUG_VIEW'):
        app.register_blueprint(ara.views.debug, url_prefix='/debug')


def configure_app(app, config):
    app.config.from_object(ara.config)

    if config is not None:
        app.config.from_object(config)

    app.config.from_envvar('ARA_CONFIG', silent=True)


def configure_dirs(app):
    if not os.path.isdir(app.config['ARA_DIR']):
        os.makedirs(app.config['ARA_DIR'], mode=0o700)


def configure_db(app):
    """
    0.10 is the first version of ARA that ships with a stable database schema.
    We can identify a database that originates from before this by checking if
    there is an alembic revision available.
    If there is no alembic revision available, assume we are running the first
    revision which contains the latest state of the database prior to this.
    """
    db.init_app(app)
    log = logging.getLogger(app.logger_name)

    if app.config.get('ARA_AUTOCREATE_DATABASE'):
        with app.app_context():
            migrations = app.config['DB_MIGRATIONS']
            flask_migrate.Migrate(app, db, directory=migrations)
            config = app.extensions['migrate'].migrate.get_config(migrations)

            # Verify if the database tables have been created at all
            inspector = Inspector.from_engine(db.engine)
            if len(inspector.get_table_names()) == 0:
                log.info('Initializing new DB from scratch')
                flask_migrate.upgrade(directory=migrations)

            # Get current alembic head revision
            script = ScriptDirectory.from_config(config)
            head = script.get_current_head()

            # Get current revision, if available
            context = MigrationContext.configure(db.engine)
            current = context.get_current_revision()

            if not current:
                log.info('Unstable DB schema, stamping original revision')
                flask_migrate.stamp(directory=migrations,
                                    revision='da9459a1f71c')

            if head != current:
                log.info('DB schema out of date, upgrading')
                flask_migrate.upgrade(directory=migrations)


def configure_logging(app):
    if app.config['ARA_LOG_FILE']:
        handler = logging.FileHandler(app.config['ARA_LOG_FILE'])
        # Set the ARA log format or fall back to the flask debugging format
        handler.setFormatter(
            logging.Formatter(app.config.get(
                'ARA_LOG_FORMAT', flask_logging.DEBUG_LOG_FORMAT)))
        logger = logging.getLogger(app.logger_name)
        logger.setLevel(app.config['ARA_LOG_LEVEL'])
        del logger.handlers[:]
        logger.addHandler(handler)
