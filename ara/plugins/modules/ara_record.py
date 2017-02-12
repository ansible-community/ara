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
