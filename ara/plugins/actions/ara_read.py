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
    from ara.webapp import create_app
    app = create_app()
    HAS_ARA = True
except ImportError:
    HAS_ARA = False

DOCUMENTATION = '''
---
module: ara_read
short_description: Ansible module to read recorded persistent data with ARA.
version_added: "2.0"
author: "RDO Community <rdo-list@redhat.com>"
description:
    - Ansible module to read recorded persistent data with ARA.
options:
    key:
        description:
            - Name of the key to read from
        required: true

requirements:
    - "python >= 2.6"
    - "ara >= 0.10.0"
'''

EXAMPLES = '''
# Write data
- ara_record:
    key: "foo"
    value: "bar"

# Read data
- ara_read:
    key: "foo"
  register: foo

# Use data
- debug:
    msg: "{{ item }}""
  with_items:
    - foo.key
    - foo.value
    - foo.type
    - foo.playbook_id
'''


class ActionModule(ActionBase):
    ''' Read from recorded persistent data as key/value pairs in ARA '''

    TRANSFERS_FILES = False
    VALID_ARGS = frozenset(('key',))

    def get_key(self, playbook_id, key):
        try:
            data = (models.Data.query
                    .filter_by(key=key)
                    .filter_by(playbook_id=playbook_id)
                    .one())
        except models.NoResultFound:
            return False

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

        required = ['key']
        for parameter in required:
            if not self._task.args.get(parameter):
                result['failed'] = True
                result['msg'] = "{} parameter is required".format(parameter)
                return result

        # Retrieve the persisted playbook_id from tmpfile
        tmpfile = os.path.join(app.config['ARA_TMP_DIR'], 'ara.json')
        with open(tmpfile) as file:
            data = json.load(file)
        playbook_id = data['playbook']['id']

        try:
            data = self.get_key(playbook_id, key)
            if data:
                result['key'] = data.key
                result['value'] = data.value
                result['type'] = data.type
                result['playbook_id'] = data.playbook_id
            msg = "Sucessfully read data for the key {0}".format(data.key)
            result['msg'] = msg
        except Exception as e:
            result['key'] = None
            result['value'] = None
            result['type'] = None
            result['playbook_id'] = None
            result['failed'] = True
            msg = "Could not read data for key {0}: {1}".format(key, str(e))
            result['msg'] = msg
        return result
