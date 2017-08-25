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

import os
import xstatic.main
import xstatic.pkg.bootstrap_scss
import xstatic.pkg.datatables
import xstatic.pkg.jquery
import xstatic.pkg.patternfly
import xstatic.pkg.patternfly_bootstrap_treeview

from ansible import __version__ as ansible_version
from ansible.constants import get_config
from ansible.constants import load_config_file
from distutils.version import LooseVersion


def _ara_config(config, key, env_var, default=None, section='ara',
                value_type=None):
    """
    Wrapper around Ansible's get_config backward/forward compatibility
    """
    if default is None:
        try:
            # We're using env_var as keys in the DEFAULTS dict
            default = DEFAULTS.get(env_var)
        except KeyError as e:
            msg = 'There is no default value for {0}: {1}'.format(key, str(e))
            raise KeyError(msg)

    # >= 2.3.0.0 (NOTE: Ansible trunk versioning scheme has 3 digits, not 4)
    if LooseVersion(ansible_version) >= LooseVersion('2.3.0'):
        return get_config(config, section, key, env_var, default,
                          value_type=value_type)

    # < 2.3.0.0 compatibility
    if value_type is None:
        return get_config(config, section, key, env_var, default)

    args = {
        'boolean': dict(boolean=True),
        'integer': dict(integer=True),
        'list': dict(islist=True),
        'tmppath': dict(istmppath=True)
    }
    return get_config(config, section, key, env_var, default,
                      **args[value_type])


DEFAULTS = {
    'ARA_AUTOCREATE_DATABASE': True,
    'ARA_DIR': os.path.expanduser('~/.ara'),
    'ARA_ENABLE_DEBUG_VIEW': False,
    'ARA_HOST': '127.0.0.1',
    'ARA_IGNORE_EMPTY_GENERATION': True,
    'ARA_IGNORE_MIMETYPE_WARNINGS': True,
    'ARA_IGNORE_PARAMETERS': ['extra_vars'],
    'ARA_LOG_CONFIG': None,
    'ARA_LOG_FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'ARA_LOG_LEVEL': 'INFO',
    'ARA_PATH_MAX': 40,
    'ARA_PLAYBOOK_OVERRIDE': None,
    'ARA_PLAYBOOK_PER_PAGE': 10,
    'ARA_PORT': '9191',
    'ARA_RESULT_PER_PAGE': 25,
    'ARA_SQL_DEBUG': False,
    'ARA_TMP_DIR': os.path.expanduser('~/.ansible/tmp')
}

# Bootstrap Ansible configuration
config, path = load_config_file()

# Some defaults need to be based on top of a "processed" ARA_DIR
ARA_DIR = _ara_config(config, 'dir', 'ARA_DIR')
database_path = os.path.join(ARA_DIR, 'ansible.sqlite')
DEFAULTS.update({
    'ARA_LOG_FILE': os.path.join(ARA_DIR, 'ara.log'),
    'ARA_DATABASE': 'sqlite:///{}'.format(database_path)
})

ARA_AUTOCREATE_DATABASE = _ara_config(config, 'autocreate_database',
                                      'ARA_AUTOCREATE_DATABASE',
                                      value_type='boolean')
ARA_ENABLE_DEBUG_VIEW = _ara_config(config, 'enable_debug_view',
                                    'ARA_ENABLE_DEBUG_VIEW',
                                    value_type='boolean')
ARA_HOST = _ara_config(config, 'host', 'ARA_HOST')
ARA_IGNORE_PARAMETERS = _ara_config(config, 'ignore_parameters',
                                    'ARA_IGNORE_PARAMETERS',
                                    value_type='list')
ARA_LOG_CONFIG = _ara_config(config, 'logconfig', 'ARA_LOG_CONFIG')
ARA_LOG_FILE = _ara_config(config, 'logfile', 'ARA_LOG_FILE')
ARA_LOG_FORMAT = _ara_config(config, 'logformat', 'ARA_LOG_FORMAT')
ARA_LOG_LEVEL = _ara_config(config, 'loglevel', 'ARA_LOG_LEVEL')
ARA_PLAYBOOK_OVERRIDE = _ara_config(config, 'playbook_override',
                                    'ARA_PLAYBOOK_OVERRIDE',
                                    value_type='list')
ARA_PLAYBOOK_PER_PAGE = _ara_config(config, 'playbook_per_page',
                                    'ARA_PLAYBOOK_PER_PAGE',
                                    value_type='integer')
ARA_PORT = _ara_config(config, 'port', 'ARA_PORT')
ARA_RESULT_PER_PAGE = _ara_config(config, 'result_per_page',
                                  'ARA_RESULT_PER_PAGE',
                                  value_type='integer')
ARA_TMP_DIR = _ara_config(config, 'local_tmp', 'ANSIBLE_LOCAL_TEMP',
                          default=DEFAULTS['ARA_TMP_DIR'],
                          section='defaults',
                          value_type='tmppath')

# Static generation with flask-frozen
ARA_IGNORE_EMPTY_GENERATION = _ara_config(config,
                                          'ignore_empty_generation',
                                          'ARA_IGNORE_EMPTY_GENERATION',
                                          value_type='boolean')
FREEZER_DEFAULT_MIMETYPE = 'text/html'
FREEZER_IGNORE_MIMETYPE_WARNINGS = _ara_config(config,
                                               'ignore_mimetype_warnings',
                                               'ARA_IGNORE_MIMETYPE_WARNINGS',
                                               value_type='boolean')
FREEZER_RELATIVE_URLS = True
FREEZER_IGNORE_404_NOT_FOUND = True

# SQLAlchemy/Alembic settings
SQLALCHEMY_DATABASE_URI = _ara_config(config, 'database', 'ARA_DATABASE')
SQLALCHEMY_ECHO = _ara_config(config, 'sqldebug',
                              'ARA_SQL_DEBUG',
                              value_type='boolean')
SQLALCHEMY_TRACK_MODIFICATIONS = False

INSTALL_PATH = os.path.dirname(os.path.realpath(__file__))
DB_MIGRATIONS = os.path.join(INSTALL_PATH, 'db')

# Xstatic configuration
treeview = xstatic.pkg.patternfly_bootstrap_treeview
XSTATIC = dict(
    bootstrap=xstatic.main.XStatic(xstatic.pkg.bootstrap_scss).base_dir,
    datatables=xstatic.main.XStatic(xstatic.pkg.datatables).base_dir,
    jquery=xstatic.main.XStatic(xstatic.pkg.jquery).base_dir,
    patternfly=xstatic.main.XStatic(xstatic.pkg.patternfly).base_dir,
    patternfly_bootstrap_treeview=xstatic.main.XStatic(treeview).base_dir,
)
