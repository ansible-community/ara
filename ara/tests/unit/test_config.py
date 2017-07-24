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

from ara.tests.unit.common import TestAra


class TestConfig(TestAra):
    """ Tests the config module """
    def setUp(self):
        super(TestConfig, self).setUp()

    def tearDown(self):
        super(TestConfig, self).tearDown()

    def test_default_config(self):
        """ Ensure we have expected default parameters """
        keys = [
            'ARA_AUTOCREATE_DATABASE',
            'ARA_DIR',
            'ARA_ENABLE_DEBUG_VIEW',
            'ARA_HOST',
            'ARA_IGNORE_EMPTY_GENERATION',
            'ARA_LOG_FILE',
            'ARA_LOG_FORMAT',
            'ARA_LOG_LEVEL',
            'ARA_PORT',
            'ARA_PLAYBOOK_OVERRIDE',
            'ARA_PLAYBOOK_PER_PAGE',
            'ARA_RESULT_PER_PAGE',
        ]

        defaults = self.app.config['DEFAULTS']

        for key in keys:
            self.assertEqual(defaults[key],
                             self.app.config[key])

        self.assertEqual(defaults['ARA_DATABASE'],
                         self.app.config['SQLALCHEMY_DATABASE_URI'])
        self.assertEqual(defaults['ARA_SQL_DEBUG'],
                         self.app.config['SQLALCHEMY_ECHO'])
        self.assertEqual(defaults['ARA_TMP_DIR'],
                         os.path.split(self.app.config['ARA_TMP_DIR'])[:-1][0])
        self.assertEqual(defaults['ARA_IGNORE_MIMETYPE_WARNINGS'],
                         self.app.config['FREEZER_IGNORE_MIMETYPE_WARNINGS'])

    # TODO:
    # - Add tests for config from hash (create_app(config))
    # - Possibly test config from envvars
    #   ( Needs config.py not to configure things at import time )
    # - Mock out or control filesystem operations (i.e, webapp.configure_dirs)
