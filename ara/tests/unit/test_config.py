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

from ara.config.base import BaseConfig
from ara.setup import path as ara_location

from ara.tests.unit.common import TestAra


class TestConfig(TestAra):
    """ Tests the config module """
    def setUp(self):
        super(TestConfig, self).setUp()

    def tearDown(self):
        super(TestConfig, self).tearDown()

    # TODO: Improve those
    def test_config_base(self):
        base_config = BaseConfig()
        db = 'sqlite:///%s/ansible.sqlite' % os.path.expanduser('~/.ara')
        defaults = {
            'FREEZER_IGNORE_MIMETYPE_WARNINGS': True,
            'FREEZER_DEFAULT_MIMETYPE': 'text/html',
            'FREEZER_IGNORE_404_NOT_FOUND': True,
            'ARA_DIR': os.path.expanduser('~/.ara'),
            'SQLALCHEMY_DATABASE_URI': db,
            'APPLICATION_ROOT': '/',
            'ARA_HOST': '127.0.0.1',
            'ARA_AUTOCREATE_DATABASE': True,
            'ARA_PORT': "9191",
            'ARA_DATABASE': db,
            'ARA_IGNORE_EMPTY_GENERATION': True,
            'ARA_IGNORE_FACTS': [
                'ansible_env'
            ],
            'ARA_IGNORE_PARAMETERS': [
                'extra_vars'
            ],
            'FREEZER_RELATIVE_URLS': True,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SQLALCHEMY_ECHO': False,
            'SQLALCHEMY_POOL_SIZE': None,
            'SQLALCHEMY_POOL_TIMEOUT': None,
            'SQLALCHEMY_POOL_RECYCLE': None,
            'DB_MIGRATIONS': os.path.join(ara_location, 'db')
        }

        for key, value in base_config.config.items():
            assert value == defaults[key]
