# Copyright (c) 2025 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible.playbook.play import Play
from ansible.plugins.action import ActionBase

from ara.clients import utils as client_utils

DOCUMENTATION = """
---
module: ara_label
short_description: Manages labels on playbooks recorded by ara
version_added: "1.7.3"
author: "David Moreau-Simard <opensource@rfc2549.ca>"
description:
    - Adds or removes labels on playbooks recorded by ara
options:
    playbook_id:
        description:
            - id of the playbook to manage labels on
            - if not set, the module will use the ongoing playbook's id
        required: false
    labels:
        description:
            - A list of labels to add to (or remove from) the playbook
        required: true
    state:
        description:
            - Whether the labels should be added (present) or removed (absent)
        default: present

requirements:
    - "python >= 3.8"
    - "ara >= 1.7.3"
"""

EXAMPLES = """
- name: Add a static label to this playbook (the one that is running)
  # Note: By default Ansible will run this task on every host.
  # Consider the use case and declare 'run_once: true' when there is no need to
  # run this task more than once.
  # This might sound obvious but it avoids updating the same labels 100 times
  # if there are 100 hosts, incurring a performance penalty needlessly.
  run_once: true
  ara_label:
    state: present
    labels:
      - state:running

- name: Add dynamically templated labels to this playbook
  ara_label:
    state: present
    labels:
      - "git:{{ lookup('git -C {{ playbook_dir }} rev-parse HEAD') }}"
      - "os:{{ ansible_distribution }}-{{ ansible_distribution_version }}"

- name: Add labels to a specific playbook
  ara_label:
    state: present
    playbook_id: 1
    labels:
      - state:deployed

- name: Remove labels from the running playbook (if they exist)
  ara_label:
    state: absent
    labels:
      - state:running
"""

RETURN = """
playbook:
    description: ID of the playbook the data was recorded in
    returned: on success
    type: int
    sample: 1
labels:
    description: an updated list of labels
    returned: on success
    type: list
    sample: ["dev","os:Fedora-41"]
"""


class ActionModule(ActionBase):
    """Manages labels on a playbook recorded by ara"""

    TRANSFERS_FILES = False
    # Note: BYPASS_HOST_LOOP functions like a forced "run_once" on a task
    # We considered setting this as the default but decided against it for now.
    # Discussion here: https://codeberg.org/ansible-community/ara/pull/274
    # BYPASS_HOST_LOOP = True
    VALID_ARGS = frozenset(("state", "playbook_id", "labels"))

    def __init__(self, *args, **kwargs):
        super(ActionModule, self).__init__(*args, **kwargs)
        self.client = client_utils.active_client()

    # TODO: We should move code like this in some form of common util library
    # this is largely taken how the callback does it
    def _set_playbook_labels(self, playbook, labels):
        # Labels may not exceed 255 characters
        # https://codeberg.org/ansible-community/ara/issues/185
        # https://codeberg.org/ansible-community/ara/issues/265
        expected_labels = []
        for label in labels:
            if len(label) >= 255:
                label = label[:254]
            expected_labels.append(label)

        changed = False
        current_labels = [label["name"] for label in playbook["labels"]]
        if sorted(current_labels) != sorted(expected_labels):
            playbook = self.client.patch("/api/v1/playbooks/%s" % playbook["id"], labels=expected_labels)
            changed = True

        return changed, playbook["labels"]

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        for arg in self._task.args:
            if arg not in self.VALID_ARGS:
                result = {"failed": True, "msg": "{0} is not a valid option.".format(arg)}
                return result

        result = super(ActionModule, self).run(tmp, task_vars)

        state = self._task.args.get("state", "present")
        playbook_id = self._task.args.get("playbook_id", None)
        labels = self._task.args.get("labels", None)

        required = ["labels"]
        for parameter in required:
            if not self._task.args.get(parameter):
                result["failed"] = True
                result["msg"] = "Parameter '{0}' is required".format(parameter)
                return result

        if playbook_id is None:
            # Retrieve the playbook id by working our way up from the task to find
            # the play uuid. Once we have the play uuid, we can find the playbook.
            parent = self._task
            while not isinstance(parent._parent._play, Play):
                parent = parent._parent

            play = self.client.get("/api/v1/plays?uuid=%s" % parent._parent._play._uuid)
            playbook_id = play["results"][0]["playbook"]

        playbook = self.client.get("/api/v1/playbooks/%s" % playbook_id)
        current_labels = [label["name"] for label in playbook["labels"]]

        if state == "present":
            expected_labels = current_labels + labels
        elif state == "absent":
            expected_labels = current_labels
            for label in labels:
                if label in current_labels:
                    expected_labels.remove(label)

        try:
            changed, labels = self._set_playbook_labels(playbook, expected_labels)
            result["changed"] = changed
            result["labels"] = [label["name"] for label in labels]
            result["playbook_id"] = playbook_id
            if result["changed"]:
                result["msg"] = "ara playbook labels updated."
            else:
                result["msg"] = "ara playbook labels unchanged."
        except Exception as e:
            result["failed"] = True
            result["msg"] = "An error occurred when updating playbook labels: %s" % str(e)
        return result
