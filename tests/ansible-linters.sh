#!/bin/bash
#  Copyright (c) 2017 Red Hat, Inc.
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

set -ex

export ANSIBLE_ACTION_PLUGINS="ara/plugins/actions"
export ANSIBLE_LIBRARY="ara/plugins/modules"

# Some tests only work on certain versions of Ansible.
# Use Ansible's pseudo semver to determine if we can run something.
function semver_compare {
    cat << EOF | python
from __future__ import print_function
import sys
from distutils.version import LooseVersion

print(LooseVersion('${1}') ${2} LooseVersion('${3}'))
EOF
}

find ara/tests/integration ! -path '*import*.yml' -regex '.*.y[a]?ml' \
    | xargs -I file ansible-lint file

find ara/tests/integration -maxdepth 1 ! -path '*import*.yml' -regex '.*.y[a]?ml' \
    | xargs -I file ansible-playbook -i 'localhost,' --syntax-check file

ansible_version=$(ansible --version | awk '/^ansible/ {print $2}')

if [[ $(semver_compare "${ansible_version}" ">=" "2.4.0.0") == "True" ]]; then
    ansible-playbook --syntax-check ara/tests/integration/import.yml
    ansible-lint ara/tests/integration/import.yml
    ansible-playbook -vv ara/tests/integration/import.yml
fi
