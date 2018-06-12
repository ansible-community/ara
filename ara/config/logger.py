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

# Note: This file tries to import itself if it's named logging, thus, logger.

import logging
import logging.config
import os
import yaml
from ara.config.compat import ara_config


DEFAULT_LOG_CONFIG = """
---
version: 1
disable_existing_loggers: false
formatters:
    ara_standard:
        format: '%(asctime)s %(levelname)s %(name)s: %(message)s'
handlers:
    ara_console:
        class: logging.StreamHandler
        formatter: ara_standard
        level: INFO
        stream: ext://sys.stdout
    ara_file:
        class: logging.handlers.TimedRotatingFileHandler
        formatter: ara_standard
        level: {level}
        filename: '{dir}/{file}'
        when: 'midnight'
        interval: 1
        backupCount: 30
loggers:
    ara:
        handlers:
            - ara_file
        level: {level}
        propagate: 0
    alembic:
        handlers:
            - ara_console
            - ara_file
        level: WARN
        propagate: 0
    sqlalchemy.engine:
        handlers:
            - ara_file
        level: WARN
        propagate: 0
    werkzeug:
        handlers:
            - ara_console
            - ara_file
        level: INFO
        propagate: 0
"""


class LogConfig(object):
    def __init__(self):
        default_dir = ara_config('dir', 'ARA_DIR',
                                 os.path.expanduser('~/.ara'))
        self.ARA_LOG_CONFIG = ara_config(
            'logconfig', 'ARA_LOG_CONFIG', os.path.join(default_dir,
                                                        'logging.yml')
        )
        self.ARA_LOG_DIR = ara_config('logdir', 'ARA_LOG_DIR', default_dir)
        self.ARA_LOG_FILE = ara_config('logfile', 'ARA_LOG_FILE', 'ara.log')
        self.ARA_LOG_LEVEL = ara_config('loglevel', 'ARA_LOG_LEVEL', 'INFO')
        if self.ARA_LOG_LEVEL == 'DEBUG':
            self.ARA_ENABLE_DEBUG_VIEW = True
        else:
            self.ARA_ENABLE_DEBUG_VIEW = False

    @property
    def config(self):
        """ Returns a dictionary for the loaded configuration """
        return {
            key: self.__dict__[key]
            for key in dir(self)
            if key.isupper()
        }


def setup_logging(config=None):
    if config is None:
        config = LogConfig().config

    if not os.path.isdir(config['ARA_LOG_DIR']):
        os.makedirs(config['ARA_LOG_DIR'], mode=0o750)

    if not os.path.exists(config['ARA_LOG_CONFIG']):
        if not config.get('ARA_LOG_FILE'):
            config['ARA_LOG_FILE'] = 'ara.log'
        default_config = DEFAULT_LOG_CONFIG.format(
            dir=config['ARA_LOG_DIR'],
            file=config['ARA_LOG_FILE'],
            level=config['ARA_LOG_LEVEL']
        )
        with open(config['ARA_LOG_CONFIG'], 'w') as log_config:
            log_config.write(default_config.lstrip())

    ext = os.path.splitext(config['ARA_LOG_CONFIG'])[1]
    if ext in ('.yml', '.yaml', '.json'):
        # yaml.safe_load can load json as well as yaml
        logging.config.dictConfig(
            yaml.safe_load(open(config['ARA_LOG_CONFIG'], 'r'))
        )
    else:
        logging.config.fileConfig(
            config['ARA_LOG_CONFIG'],
            disable_existing_loggers=False
        )

    logger = logging.getLogger('ara.config.logging')
    msg = 'Logging: Level {level} from {config}, logging to {dir}/{file}'
    msg = msg.format(
        level=config['ARA_LOG_LEVEL'],
        config=config['ARA_LOG_CONFIG'],
        dir=config['ARA_LOG_DIR'],
        file=config['ARA_LOG_FILE'],
    )
    logger.debug(msg)
