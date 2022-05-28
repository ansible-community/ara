# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

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
