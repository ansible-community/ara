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

import sys

from ansible import __version__ as ansible_version
from ara import __release__ as ara_release
from ara import models


def configure_context_processors(app):
    @app.context_processor
    def ctx_add_nav_data():
        """
        Returns standard data that will be available in every template view.
        """
        try:
            models.Playbook.query.one()
            empty_database = False
        except models.MultipleResultsFound:
            empty_database = False
        except models.NoResultFound:
            empty_database = True

        # Get python version info
        major, minor, micro, release, serial = sys.version_info

        return dict(ara_version=ara_release,
                    ansible_version=ansible_version,
                    python_version="{0}.{1}".format(major, minor),
                    empty_database=empty_database)
