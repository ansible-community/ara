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
