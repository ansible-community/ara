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

import json
import os

from ansible.plugins.action import ActionBase

try:
    from ara import models
    from ara.models import db
    from ara.webapp import create_app
    app = create_app()
    HAS_ARA = True
except ImportError:
    HAS_ARA = False

DOCUMENTATION = '''
---
module: ara_record
short_description: Ansible module to record persistent data with ARA.
version_added: "2.0"
author: "RDO Community <rdo-list@redhat.com>"
description:
    - Ansible module to record persistent data with ARA.
options:
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
    - "python >= 2.6"
    - "ara >= 0.10.0"
'''

EXAMPLES = '''
# Write static data
- ara_record:
    key: "foo"
    value: "bar"

# Write dynamic data
- shell: cd dev && git rev-parse HEAD
  register: git_version
  delegate_to: localhost

- ara_record:
    key: "git_version"
    value: "{{ git_version.stdout }}"

# Write data with a type (otherwise defaults to "text")
# This changes the behavior on how the value is presented in the web interface
- ara_record:
    key: "{{ item.key }}"
    value: "{{ item.value }}"
    type: "{{ item.type }}"
  with_items:
    - { key: "log", value: "error", type: "text" }
    - { key: "website", value: "http://domain.tld", type: "url" }
    - { key: "data", value: "{ 'key': 'value' }", type: "json" }
    - { key: "somelist", value: ['one', 'two'], type: "list" }
    - { key: "somedict", value: {'key': 'value' }, type: "dict" }
'''


class ActionModule(ActionBase):
    ''' Record persistent data as key/value pairs in ARA '''

    TRANSFERS_FILES = False
    VALID_ARGS = frozenset(('key', 'value', 'type'))
    VALID_TYPES = ['text', 'url', 'json', 'list', 'dict']

    def create_or_update_key(self, playbook_id, key, value, type):
        try:
            data = (models.Data.query
                    .filter_by(key=key)
                    .filter_by(playbook_id=playbook_id)
                    .one())
            data.value = value
            data.type = type
        except models.NoResultFound:
            data = models.Data(playbook_id=playbook_id,
                               key=key,
                               value=value,
                               type=type)
        db.session.add(data)
        db.session.commit()

        return data

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        if not HAS_ARA:
            result = {
                "failed": True,
                "msg": "ARA is required to run this module."
            }
            return result

        for arg in self._task.args:
            if arg not in self.VALID_ARGS:
                result = {
                    "failed": True,
                    "msg": "'{0}' is not a valid option.".format(arg)
                }
                return result

        result = super(ActionModule, self).run(tmp, task_vars)

        key = self._task.args.get('key', None)
        value = self._task.args.get('value', None)
        type = self._task.args.get('type', 'text')

        required = ['key', 'value']
        for parameter in required:
            if not self._task.args.get(parameter):
                result['failed'] = True
                result['msg'] = "Parameter '{0}' is required".format(parameter)
                return result

        if type not in self.VALID_TYPES:
            result['failed'] = True
            msg = "Type '{0}' is not supported, choose one of: {1}".format(
                type, ", ".join(self.VALID_TYPES)
            )
            result['msg'] = msg
            return result

        # Retrieve the persisted playbook_id from tmpfile
        tmpfile = os.path.join(app.config['ARA_TMP_DIR'], 'ara.json')
        with open(tmpfile) as file:
            data = json.load(file)
        playbook_id = data['playbook']['id']

        try:
            self.create_or_update_key(playbook_id, key, value, type)
            result['msg'] = "Data recorded in ARA for this playbook."
        except Exception as e:
            result['failed'] = True
            result['msg'] = "Data not recorded in ARA: {0}".format(str(e))
        return result
