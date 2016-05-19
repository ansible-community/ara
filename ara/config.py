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

from ansible.constants import get_config, load_config_file

DEFAULT_ARA_DIR = os.path.expanduser('~/.ara')
DEFAULT_DATABASE_PATH = os.path.join(DEFAULT_ARA_DIR, 'ansible.sqlite')
DEFAULT_DATABASE = 'sqlite:///{}'.format(DEFAULT_DATABASE_PATH)
DEFAULT_ARA_LOGFILE = os.path.join(DEFAULT_ARA_DIR, 'ara.log')
DEFAULT_ARA_LOG_LEVEL = 'INFO'
DEFAULT_ARA_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DEFAULT_ARA_SQL_DEBUG = False
DEFAULT_ARA_PATH_MAX = 30

config, path = load_config_file()
ARA_DIR = get_config(config, 'ara', 'dir', 'ARA_DIR', DEFAULT_ARA_DIR)
ARA_DATABASE = get_config(config, 'ara', 'database', 'ARA_DATABASE',
                          DEFAULT_DATABASE)
ARA_LOG = get_config(config, 'ara', 'logfile', 'ARA_LOGFILE',
                     DEFAULT_ARA_LOGFILE)
ARA_LOG_LEVEL = get_config(config, 'ara', 'loglevel', 'ARA_LOG_LEVEL',
                           DEFAULT_ARA_LOG_LEVEL)
ARA_LOG_FORMAT = get_config(config, 'ara', 'logformat', 'ARA_LOG_FORMAT',
                            DEFAULT_ARA_LOG_FORMAT)
ARA_SQL_DEBUG = get_config(config, 'ara', 'sqldebug', 'ARA_SQL_DEBUG',
                           DEFAULT_ARA_SQL_DEBUG)
ARA_PATH_MAX = get_config(config, 'ara', 'path_max',
                          'ARA_PATH_MAX', DEFAULT_ARA_PATH_MAX)
