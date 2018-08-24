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

import os
from ara.config.compat import ara_config
from ara.setup import path as ara_location


class BaseConfig(object):
    def __init__(self):
        self.ARA_DIR = ara_config(
            'dir',
            'ARA_DIR',
            os.path.expanduser('~/.ara')
        )
        database_path = os.path.join(self.ARA_DIR, 'ansible.sqlite')
        self.ARA_DATABASE = ara_config(
            'database',
            'ARA_DATABASE',
            'sqlite:///%s' % database_path
        )
        self.ARA_AUTOCREATE_DATABASE = ara_config(
            'autocreate_database',
            'ARA_AUTOCREATE_DATABASE',
            True,
            value_type='boolean'
        )
        self.APPLICATION_ROOT = ara_config(
            'application_root',
            'ARA_APPLICATION_ROOT',
            '/'
        )
        self.SQLALCHEMY_DATABASE_URI = self.ARA_DATABASE
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.SQLALCHEMY_ECHO = ara_config(
            'sqlalchemy_echo',
            'SQLALCHEMY_ECHO',
            False,
            value_type='boolean'
        )
        self.SQLALCHEMY_POOL_SIZE = ara_config(
            'sqlalchemy_pool_size',
            'SQLALCHEMY_POOL_SIZE',
            None,
            value_type='integer'
        )
        self.SQLALCHEMY_POOL_TIMEOUT = ara_config(
            'sqlalchemy_pool_timeout',
            'SQLALCHEMY_POOL_TIMEOUT',
            None,
            value_type='integer'
        )
        self.SQLALCHEMY_POOL_RECYCLE = ara_config(
            'sqlalchemy_pool_recycle',
            'SQLALCHEMY_POOL_RECYCLE',
            None,
            value_type='integer'
        )
        self.DB_MIGRATIONS = os.path.join(ara_location, 'db')

        self.ARA_HOST = ara_config('host', 'ARA_HOST', '127.0.0.1')
        self.ARA_PORT = ara_config('port', 'ARA_PORT', '9191')
        self.ARA_IGNORE_PARAMETERS = ara_config(
            'ignore_parameters',
            'ARA_IGNORE_PARAMETERS',
            ['extra_vars'],
            value_type='list'
        )
        self.ARA_IGNORE_FACTS = ara_config(
            'ignore_facts',
            'ARA_IGNORE_FACTS',
            ['ansible_env'],
            value_type='list'
        )

        # Static generation with flask-frozen
        self.ARA_IGNORE_EMPTY_GENERATION = ara_config(
            'ignore_empty_generation',
            'ARA_IGNORE_EMPTY_GENERATION',
            True,
            value_type='boolean'
        )
        self.FREEZER_DEFAULT_MIMETYPE = 'text/html'
        self.FREEZER_IGNORE_MIMETYPE_WARNINGS = ara_config(
            'ignore_mimetype_warnings',
            'ARA_IGNORE_MIMETYPE_WARNINGS',
            True,
            value_type='boolean'
        )
        self.FREEZER_RELATIVE_URLS = True
        self.FREEZER_IGNORE_404_NOT_FOUND = True

    @property
    def config(self):
        """ Returns a dictionary for the loaded configuration """
        return {
            key: self.__dict__[key]
            for key in dir(self)
            if key.isupper()
        }
