# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible.playbook.play import Play
from ansible.plugins.action import ActionBase

from ara.clients import utils as client_utils

DOCUMENTATION = """
---
module: ara_record
short_description: Ansible module to record persistent data with ARA.
version_added: "2.0"
author: "David Moreau-Simard <dmsimard@redhat.com>"
description:
    - Ansible module to record persistent data with ARA.
options:
    playbook_id:
        description:
            - id of the playbook to write the key to
            - if not set, the module will use the ongoing playbook's id
        required: false
    key:
        description:
            - Name of the key to write data to
        required: true
    value:
        description:
            - Value of the key written to
        required: true
    type:
        description:
            - Type of the key
        choices: [text, url, json, list, dict]
        default: text

requirements:
    - "python >= 3.5"
    - "ara >= 1.0.0"
"""

EXAMPLES = """
- name: Associate specific data to a key for a playbook
  ara_record:
    key: "foo"
    value: "bar"

- name: Associate data to a playbook that previously ran
  ara_record:
    playbook_id: 21
    key: logs
    value: "{{ lookup('file', '/var/log/ansible.log') }}"
    type: text

- name: Retrieve the git version of the development repository
  shell: cd dev && git rev-parse HEAD
  register: git_version
  delegate_to: localhost

- name: Record and register the git version of the playbooks
  ara_record:
    key: "git_version"
    value: "{{ git_version.stdout }}"
  register: version

- name: Print recorded data
  debug:
    msg: "{{ version.playbook_id }} - {{ version.key }}: {{ version.value }}

# Write data with a type (otherwise defaults to "text")
# This changes the behavior on how the value is presented in the web interface
- name: Record different formats of things
  ara_record:
    key: "{{ item.key }}"
    value: "{{ item.value }}"
    type: "{{ item.type }}"
  with_items:
    - { key: "log", value: "error", type: "text" }
    - { key: "website", value: "http://domain.tld", type: "url" }
    - { key: "data", value: "{ 'key': 'value' }", type: "json" }
    - { key: "somelist", value: ['one', 'two'], type: "list" }
    - { key: "somedict", value: {'key': 'value' }, type: "dict" }
"""


RETURN = """
playbook:
    description: ID of the playbook the data was recorded in
    returned: on success
    type: int
    sample: 1
key:
    description: Key where the record is saved
    returned: on success
    type: str
    sample: log_url
value:
    description: Value of the key
    returned: on success
    type: complex
    sample: http://logurl
type:
    description: Type of the key
    returned: on success
    type: string
    sample: url
created:
    description: Date the record was created (ISO-8601)
    returned: on success
    type: str
    sample: 2018-11-15T17:27:41.597234Z
updated:
    description: Date the record was updated (ISO-8601)
    returned: on success
    type: str
    sample: 2018-11-15T17:27:41.597265Z
"""


class ActionModule(ActionBase):
    """Record persistent data as key/value pairs in ARA"""

    TRANSFERS_FILES = False
    VALID_ARGS = frozenset(("playbook_id", "key", "value", "type"))
    VALID_TYPES = ["text", "url", "json", "list", "dict"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = client_utils.active_client()

    def create_or_update_key(self, playbook, key, value, type):
        changed = False
        record = self.client.get("/api/v1/records?playbook=%s&key=%s" % (playbook, key))
        if record["count"] == 0:
            # Create the record if it doesn't exist
            record = self.client.post("/api/v1/records", playbook=playbook, key=key, value=value, type=type)
            changed = True
        else:
            # Otherwise update it if the data is different (idempotency)
            old = self.client.get("/api/v1/records/%s" % record["results"][0]["id"])
            if old["value"] != value or old["type"] != type:
                record = self.client.patch("/api/v1/records/%s" % old["id"], key=key, value=value, type=type)
                changed = True
            else:
                record = old
        return record, changed

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        for arg in self._task.args:
            if arg not in self.VALID_ARGS:
                result = {"failed": True, "msg": f"{arg} is not a valid option."}
                return result

        result = super().run(tmp, task_vars)

        playbook_id = self._task.args.get("playbook_id", None)
        key = self._task.args.get("key", None)
        value = self._task.args.get("value", None)
        type = self._task.args.get("type", "text")

        required = ["key", "value"]
        for parameter in required:
            if not self._task.args.get(parameter):
                result["failed"] = True
                result["msg"] = f"Parameter '{parameter}' is required"
                return result

        if type not in self.VALID_TYPES:
            result["failed"] = True
            msg = "Type '{}' is not supported, choose one of: {}".format(type, ", ".join(self.VALID_TYPES))
            result["msg"] = msg
            return result

        if playbook_id is None:
            # Retrieve the playbook id by working our way up from the task to find
            # the play uuid. Once we have the play uuid, we can find the playbook.
            parent = self._task
            while not isinstance(parent._parent._play, Play):
                parent = parent._parent

            play = self.client.get("/api/v1/plays?uuid=%s" % parent._parent._play._uuid)
            playbook_id = play["results"][0]["playbook"]

        try:
            data, changed = self.create_or_update_key(playbook_id, key, value, type)
            result["changed"] = changed
            result["key"] = data["key"]
            result["value"] = data["value"]
            result["type"] = data["type"]
            result["playbook_id"] = data["playbook"]
            result["created"] = data["created"]
            result["updated"] = data["updated"]
            if result["changed"]:
                result["msg"] = "Record created or updated in ARA"
            else:
                result["msg"] = "Record unchanged in ARA"
        except Exception as e:
            result["changed"] = False
            result["failed"] = True
            result["msg"] = f"Record failed to be created or updated in ARA: {str(e)}"
        return result
