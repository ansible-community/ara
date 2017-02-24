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

from ansible.constants import get_config, load_config_file

DEFAULT_ARA_DIR = os.path.expanduser('~/.ara')
DEFAULT_ARA_TMP_DIR = os.path.expanduser('~/.ansible/tmp')
DEFAULT_ARA_LOG_LEVEL = 'INFO'
DEFAULT_ARA_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DEFAULT_ARA_SQL_DEBUG = False
DEFAULT_ARA_PATH_MAX = 40
DEFAULT_ARA_IGNORE_MIMETYPE_WARNINGS = True
DEFAULT_ARA_PLAYBOOK_PER_PAGE = 10
DEFAULT_ARA_RESULT_PER_PAGE = 25

config, path = load_config_file()

ARA_DIR = get_config(
    config, 'ara', 'dir', 'ARA_DIR',
    DEFAULT_ARA_DIR)
# Log/database location default to the ARA directory once we know where it is
DEFAULT_ARA_LOG_FILE = os.path.join(ARA_DIR, 'ara.log')
DEFAULT_DATABASE_PATH = os.path.join(ARA_DIR, 'ansible.sqlite')
DEFAULT_DATABASE = 'sqlite:///{}'.format(DEFAULT_DATABASE_PATH)

# Ansible >= 2.3 introduced the value_type parameter
try:
    ARA_TMP_DIR = get_config(
        config, 'defaults', 'local_tmp', 'ANSIBLE_LOCAL_TEMP',
        DEFAULT_ARA_TMP_DIR, istmppath=True)
    ARA_PLAYBOOK_OVERRIDE = get_config(
        config, 'ara', 'playbook_override', 'ARA_PLAYBOOK_OVERRIDE',
        None, islist=True)
    ARA_PLAYBOOK_PER_PAGE = get_config(
        config, 'ara', 'playbook_per_page', 'ARA_PLAYBOOK_PER_PAGE',
        DEFAULT_ARA_PLAYBOOK_PER_PAGE, integer=True
    )
    ARA_RESULT_PER_PAGE = get_config(
        config, 'ara', 'result_per_page', 'ARA_RESULT_PER_PAGE',
        DEFAULT_ARA_RESULT_PER_PAGE, integer=True
    )
except TypeError:
    ARA_TMP_DIR = get_config(
        config, 'defaults', 'local_tmp', 'ANSIBLE_LOCAL_TEMP',
        DEFAULT_ARA_TMP_DIR, value_type='tmppath')
    ARA_PLAYBOOK_OVERRIDE = get_config(
        config, 'ara', 'playbook_override', 'ARA_PLAYBOOK_OVERRIDE',
        None, value_type='list')
    ARA_PLAYBOOK_PER_PAGE = get_config(
        config, 'ara', 'playbook_per_page', 'ARA_PLAYBOOK_PER_PAGE',
        DEFAULT_ARA_PLAYBOOK_PER_PAGE, value_type='integer'
    )
    ARA_RESULT_PER_PAGE = get_config(
        config, 'ara', 'result_per_page', 'ARA_RESULT_PER_PAGE',
        DEFAULT_ARA_RESULT_PER_PAGE, value_type='integer'
    )
ARA_LOG_FILE = get_config(
    config, 'ara', 'logfile', 'ARA_LOG_FILE',
    DEFAULT_ARA_LOG_FILE)
ARA_LOG_LEVEL = get_config(
    config, 'ara', 'loglevel', 'ARA_LOG_LEVEL',
    DEFAULT_ARA_LOG_LEVEL).upper()
ARA_LOG_FORMAT = get_config(
    config, 'ara', 'logformat', 'ARA_LOG_FORMAT',
    DEFAULT_ARA_LOG_FORMAT)
ARA_PATH_MAX = get_config(
    config, 'ara', 'path_max', 'ARA_PATH_MAX',
    DEFAULT_ARA_PATH_MAX)
ARA_ENABLE_DEBUG_VIEW = get_config(
    config, 'ara', 'enable_debug_view', 'ARA_ENABLE_DEBUG_VIEW',
    False)
ARA_AUTOCREATE_DATABASE = get_config(
    config, 'ara', 'autocreate_database', 'ARA_AUTOCREATE_DATABASE',
    True)

# SQL Alchemy/Alembic
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = get_config(config, 'ara', 'database', 'ARA_DATABASE',
                                     DEFAULT_DATABASE)
SQLALCHEMY_ECHO = get_config(config, 'ara', 'sqldebug', 'ARA_SQL_DEBUG',
                             DEFAULT_ARA_SQL_DEBUG)
INSTALL_PATH = os.path.dirname(os.path.realpath(__file__))
DB_MIGRATIONS = os.path.join(INSTALL_PATH, 'db')

# Static generation
FREEZER_RELATIVE_URLS = True
FREEZER_DEFAULT_MIMETYPE = 'text/html'
FREEZER_IGNORE_MIMETYPE_WARNINGS = get_config(
    config, 'ara', 'ignore_mimetype_warnings', 'ARA_IGNORE_MIMETYPE_WARNINGS',
    DEFAULT_ARA_IGNORE_MIMETYPE_WARNINGS)
