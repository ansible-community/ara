#   Copyright 2016 Red Hat, Inc. All Rights Reserved.
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

from flask import Flask
from flask import logging as flask_logging

from ara.models import db
from ara.filters import configure_template_filters
from ara.context_processors import configure_context_processors
from ara.errorhandlers import configure_errorhandlers
import ara.views
import ara.config


DEFAULT_APP_NAME = 'ara'


views = (
    (ara.views.home, ''),
    (ara.views.file, '/file'),
    (ara.views.playbook, '/playbook'),
    (ara.views.host, '/host'),
    (ara.views.play, '/play'),
    (ara.views.task, '/task'),
    (ara.views.result, '/result'),
)


def create_app(config=None, app_name=None):
    if app_name is None:
        app_name = DEFAULT_APP_NAME

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
        os.makedirs(app.config['ARA_DIR'], mode=0700)


def configure_db(app):
    db.init_app(app)

    if app.config.get('ARA_AUTOCREATE_DATABASE'):
        with app.app_context():
            db.create_all()


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
