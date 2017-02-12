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

# This file is purposefully left empty due to an Ansible issue
# Details at: https://github.com/ansible/ansible/pull/18208

# TODO: Remove this file and update the documentation when the issue is fixed,
# released and present in all supported versions.

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
