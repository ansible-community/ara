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
import unittest

from ara import webapp as w
from ara import config as c


class TestConfig(unittest.TestCase):
    """ Tests the config module """
    def test_default_config(self):
        """ Ensure we have expected default parameters """
        app = w.create_app()

        keys = [
            'ARA_AUTOCREATE_DATABASE',
            'ARA_DIR',
            'ARA_ENABLE_DEBUG_VIEW',
            'ARA_LOG_FILE',
            'ARA_LOG_FORMAT',
            'ARA_LOG_LEVEL',
            'ARA_PLAYBOOK_OVERRIDE',
            'ARA_PLAYBOOK_PER_PAGE',
            'ARA_RESULT_PER_PAGE',
        ]

        for key in keys:
            self.assertEqual(c.DEFAULTS[key], app.config[key])

        self.assertEqual(c.DEFAULTS['ARA_DATABASE'],
                         app.config['SQLALCHEMY_DATABASE_URI'])
        self.assertEqual(c.DEFAULTS['ARA_SQL_DEBUG'],
                         app.config['SQLALCHEMY_ECHO'])
        self.assertEqual(c.DEFAULTS['ARA_TMP_DIR'],
                         os.path.split(app.config['ARA_TMP_DIR'])[:-1][0])
        self.assertEqual(c.DEFAULTS['ARA_IGNORE_MIMETYPE_WARNINGS'],
                         app.config['FREEZER_IGNORE_MIMETYPE_WARNINGS'])

    # TODO:
    # - Add tests for config from hash (create_app(config))
    # - Possibly test config from envvars
    #   ( Needs config.py not to configure things at import time )
    # - Mock out or control filesystem operations (i.e, webapp.configure_dirs)
