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
