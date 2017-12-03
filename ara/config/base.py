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
from ara.config.compat import ara_config
from ara.setup import path as ara_location


class BaseConfig(object):
    def __init__(self):
        self.ARA_DIR = ara_config('dir',
                                  'ARA_DIR',
                                  os.path.expanduser('~/.ara'))

        database_path = os.path.join(self.ARA_DIR, 'ansible.sqlite')
        self.ARA_DATABASE = ara_config(
            'database', 'ARA_DATABASE', 'sqlite:///%s' % database_path
        )
        self.ARA_AUTOCREATE_DATABASE = ara_config('autocreate_database',
                                                  'ARA_AUTOCREATE_DATABASE',
                                                  True,
                                                  value_type='boolean')
        self.SQLALCHEMY_DATABASE_URI = self.ARA_DATABASE
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.DB_MIGRATIONS = os.path.join(ara_location, 'db')

        self.ARA_HOST = ara_config('host', 'ARA_HOST', '127.0.0.1')
        self.ARA_PORT = ara_config('port', 'ARA_PORT', '9191')
        endpoint = 'http://%s:%s/api/v1' % (self.ARA_HOST, self.ARA_PORT)
        self.ARA_API_ENDPOINT = ara_config('api_endpoint',
                                           'ARA_API_ENDPOINT',
                                           endpoint)
        self.ARA_API_CLIENT = ara_config('api_client',
                                         'ARA_API_CLIENT',
                                         'offline')

        self.ARA_IGNORE_PARAMETERS = ara_config('ignore_parameters',
                                                'ARA_IGNORE_PARAMETERS',
                                                ['extra_vars'],
                                                value_type='list')

    @property
    def config(self):
        """ Returns a dictionary for the loaded configuration """
        return {
            key: self.__dict__[key]
            for key in dir(self)
            if key.isupper()
        }
