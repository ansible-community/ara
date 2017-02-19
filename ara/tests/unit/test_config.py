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

        self.assertEqual(app.config['ARA_DIR'],
                         c.DEFAULT_ARA_DIR)
        self.assertEqual(os.path.split(app.config['ARA_TMP_DIR'])[:-1][0],
                         c.DEFAULT_ARA_TMP_DIR)
        self.assertEqual(app.config['ARA_LOG_FILE'],
                         c.DEFAULT_ARA_LOG_FILE)
        self.assertEqual(app.config['ARA_LOG_LEVEL'],
                         c.DEFAULT_ARA_LOG_LEVEL)
        self.assertEqual(app.config['ARA_LOG_FORMAT'],
                         c.DEFAULT_ARA_LOG_FORMAT)
        self.assertEqual(app.config['ARA_PATH_MAX'],
                         c.DEFAULT_ARA_PATH_MAX)
        self.assertEqual(app.config['SQLALCHEMY_ECHO'],
                         c.DEFAULT_ARA_SQL_DEBUG)
        self.assertEqual(app.config['SQLALCHEMY_DATABASE_URI'],
                         c.DEFAULT_DATABASE)
        self.assertEqual(app.config['FREEZER_IGNORE_MIMETYPE_WARNINGS'],
                         c.DEFAULT_ARA_IGNORE_MIMETYPE_WARNINGS)

        self.assertEqual(app.config['ARA_ENABLE_DEBUG_VIEW'], False)
        self.assertEqual(app.config['ARA_AUTOCREATE_DATABASE'], True)

    # TODO:
    # - Add tests for config from hash (create_app(config))
    # - Possibly test config from envvars
    #   ( Needs config.py not to configure things at import time )
    # - Mock out or control filesystem operations (i.e, webapp.configure_dirs)
