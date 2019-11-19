#  Copyright (c) 2019 Red Hat, Inc.
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


from __future__ import absolute_import, division, print_function

from ansible.plugins.lookup import LookupBase

from ara.clients import utils as client_utils

__metaclass__ = type

DOCUMENTATION = """
    lookup: ara_api
    author: David Moreau-Simard (@dmsimard)
    version_added: "2.9"
    short_description: Queries the ARA API for data
    description:
        - Queries the ARA API for data
    options:
        _terms:
            description:
                - The endpoint to query
            type: list
            elements: string
            required: True
"""

EXAMPLES = """
    - debug: msg="{{ lookup('ara_api','/api/v1/playbooks/1') }}"
"""

RETURN = """
    _raw:
        description: response from query
"""


class LookupModule(LookupBase):
    def __init__(self, *args, **kwargs):
        super(LookupModule, self).__init__(*args, **kwargs)
        self.client = client_utils.active_client()

    def run(self, terms, variables, **kwargs):
        ret = []
        for term in terms:
            ret.append(self.client.get(term))

        return ret
