#  Copyright (c) 2019 Red Hat, Inc.
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

from ansible.playbook.play import Play
from ansible.plugins.action import ActionBase

from ara.clients import utils as client_utils

DOCUMENTATION = """
---
module: ara_playbook
short_description: Retrieves either a specific playbook from ARA or the one currently running
version_added: "2.9"
author: "David Moreau-Simard <dmsimard@redhat.com>"
description:
    - Retrieves either a specific playbook from ARA or the one currently running
options:
    playbook_id:
        description:
            - id of the playbook to retrieve
            - if not set, the module will use the ongoing playbook's id
        required: false

requirements:
    - "python >= 3.5"
    - "ara >= 1.4.0"
"""

EXAMPLES = """
- name: Get a specific playbook
  ara_playbook:
    playbook_id: 5
  register: playbook_query

- name: Get current playbook by not specifying a playbook id
  ara_playbook:
  register: playbook_query

- name: Do something with the playbook
  debug:
    msg: "Playbook report: http://ara_api/playbook/{{ playbook_query.playbook.id | string }}.html"
"""

RETURN = """
playbook:
    description: playbook object returned by the API
    returned: on success
    type: dict
"""


class ActionModule(ActionBase):
    """ Retrieves either a specific playbook from ARA or the one currently running """

    TRANSFERS_FILES = False
    VALID_ARGS = frozenset(("playbook_id"))

    def __init__(self, *args, **kwargs):
        super(ActionModule, self).__init__(*args, **kwargs)
        self.client = client_utils.active_client()

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        for arg in self._task.args:
            if arg not in self.VALID_ARGS:
                result = {"failed": True, "msg": "{0} is not a valid option.".format(arg)}
                return result

        result = super(ActionModule, self).run(tmp, task_vars)

        playbook_id = self._task.args.get("playbook_id", None)
        if playbook_id is None:
            # Retrieve the playbook id by working our way up from the task to find
            # the play uuid. Once we have the play uuid, we can find the playbook.
            parent = self._task
            while not isinstance(parent._parent._play, Play):
                parent = parent._parent

            play = self.client.get("/api/v1/plays?uuid=%s" % parent._parent._play._uuid)
            playbook_id = play["results"][0]["playbook"]

        result["playbook"] = self.client.get("/api/v1/playbooks/%s" % playbook_id)
        result["changed"] = False
        result["msg"] = "Queried playbook %s from ARA" % playbook_id

        return result
