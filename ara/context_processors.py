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

from ansible import __version__ as ansible_version

# TODO: Why can't I import __release__ from ara here ?
import pbr.version

# Setup version
version_info = pbr.version.VersionInfo('ara')
try:
    __version__ = version_info.version_string()
    __release__ = version_info.release_string()
except AttributeError:
    __version__ = None
    __release__ = None


def configure_context_processors(app):

    @app.context_processor
    def ctx_add_nav_data():
        '''Makes some standard data from the database available in the
        template context.'''

        ara_version = __release__

        return dict(ara_version=ara_version,
                    ansible_version=ansible_version)
