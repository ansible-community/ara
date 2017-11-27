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

# Note: This file tries to import itself if it's named logging, thus, logger.

import logging
import logging.config
import os
import yaml
from ara.config.compat import ara_config

default_dir = ara_config('dir', 'ARA_DIR', os.path.expanduser('~/.ara'))
ARA_LOG_CONFIG = ara_config(
    'logconfig', 'ARA_LOG_CONFIG', os.path.join(default_dir, 'logging.yml')
)
ARA_LOG_DIR = ara_config('logdir', 'ARA_LOG_DIR', default_dir)
ARA_LOG_FILE = ara_config('logfile', 'ARA_LOG_FILE', 'ara.log')
ARA_LOG_LEVEL = ara_config('loglevel', 'ARA_LOG_LEVEL', 'INFO')


def setup_logging():
    if not os.path.isdir(ARA_LOG_DIR):
        os.makedirs(ARA_LOG_DIR, mode=0o750)

    if not os.path.exists(ARA_LOG_CONFIG):
        default_config = """
---
version: 1
formatters:
    normal:
        format: '%(asctime)s %(levelname)s %(name)s: %(message)s'
    console:
        format: '%(asctime)s %(levelname)s %(name)s: %(message)s'
handlers:
    console:
        class: logging.StreamHandler
        formatter: console
        level: INFO
        stream: ext://sys.stdout
    normal:
        class: logging.handlers.TimedRotatingFileHandler
        formatter: normal
        level: DEBUG
        filename: '{dir}/{file}'
        when: 'midnight'
        interval: 1
        backupCount: 30
loggers:
    ara:
        handlers:
            - console
            - normal
        level: {level}
        propagate: 0
    alembic:
        handlers:
            - console
            - normal
        level: WARN
        propagate: 0
    sqlalchemy.engine:
        handlers:
            - console
            - normal
        level: WARN
        propagate: 0
    werkzeug:
        handlers:
            - console
            - normal
        level: INFO
        propagate: 0
root:
  handlers:
    - normal
  level: {level}
"""
        default_config = default_config.format(
            dir=ARA_LOG_DIR,
            file=ARA_LOG_FILE,
            level=ARA_LOG_LEVEL
        )
        with open(ARA_LOG_CONFIG, 'w') as config:
            config.write(default_config.lstrip())

    if os.path.splitext(ARA_LOG_CONFIG)[1] in ('.yml', '.yaml', '.json'):
        # yaml.safe_load can load json as well as yaml
        logging.config.dictConfig(yaml.safe_load(open(ARA_LOG_CONFIG, 'r')))
    else:
        logging.config.fileConfig(ARA_LOG_CONFIG)

    logger = logging.getLogger('ara.logging')
    msg = 'Logging: Level {level} from {config}, logging to {dir}/{file}'
    msg = msg.format(
        level=ARA_LOG_LEVEL,
        config=ARA_LOG_CONFIG,
        dir=ARA_LOG_DIR,
        file=ARA_LOG_FILE,
    )
    logger.debug(msg)
