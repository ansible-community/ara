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

function usage {
    cat << EOF
usage: ./run-tests.sh [-a|--ansible ANSIBLE_VERSION] [-a|--python PYTHON_VERSION] [-h|--help]

Runs ARA integration tests

optional arguments:
-a, --ansible      Ansible version to test with (ex: '2.3.1.0', 'devel')
                   Defaults to version in requirements.txt (latest version of Ansible)
-p, --python       Python version from a tox environment to test with (ex: 'py27', 'py35')
                   Defaults to py27
-h, --help         Prints this help dialog.
EOF
}

# Cleanup from any previous runs if necessary
function cleanup {
    [[ -e "${LOGDIR}" ]] && rm -rf "${LOGDIR}"
    [[ -e ".tox/${python_version}" ]] && rm -rf .tox/${python_version}
    mkdir -p "${LOGDIR}"
    touch ${CONSTRAINTS_FILE}
}

# Get args
ansible_version="latest"
python_version="py27"
while [ "$1" != "" ]; do
    case $1 in
        -a | --ansible )        shift
                                ansible_version=$1
                                ;;
        -p | --python )         shift
                                python_version=$1
                                ;;
        -h | --help )           usage
                                exit
                                ;;
        * )                     usage
                                exit 1
    esac
    shift
done
echo "Running ARA integration tests with Ansible ${ansible_version} on ${python_version}..."

set -ex
export PATH=$PATH:/usr/local/sbin:/usr/sbin
LOGROOT=${WORKSPACE:-/tmp/ara_tests}
LOGDIR="${LOGROOT}/logs"
SCRIPT_DIR=$(cd `dirname $0` && pwd -P)
export ANSIBLE_TMP_DIR="${LOGDIR}/ansible"
export CONSTRAINTS_FILE="${LOGDIR}/constraints.txt"

cleanup

if [[ $ARA_TEST_PGSQL == "1" ]]; then
    if [[ -z $ARA_TEST_PGSQL_USER || -z $ARA_TEST_PGSQL_PASSWORD ]]; then
        echo 'Please set $ARA_TEST_PGSQL_USER and $ARA_TEST_PGSQL_PASSWORD'
        exit 1
    fi
    DATABASE="postgresql+psycopg2://$ARA_TEST_PGSQL_USER:$ARA_TEST_PGSQL_PASSWORD@localhost:5432/ara"
else
    DATABASE="sqlite:///${LOGDIR}/ansible.sqlite"
fi

# Ensure we're running from the script directory
pushd "${SCRIPT_DIR}"

if ! [[ "${ansible_version}" =~ "latest" ]]; then
    current_version=$(grep "ansible" requirements.txt)
    echo "Will use Ansible ${ansible_version} instead of ${current_version} in tests..."
    if [[ "${ansible_version}" =~ "devel" ]]; then
        echo "git+https://github.com/ansible/ansible@devel#egg=ansible" > ${CONSTRAINTS_FILE}
    else
        echo "ansible==${ansible_version}" > ${CONSTRAINTS_FILE}
    fi
fi

# Install ARA so it can be used from a virtual environment
tox -e ${python_version} --notest
source .tox/${python_version}/bin/activate
ansible_version=$(pip freeze |awk -F== '/ansible==/ {print $2}')
ansible --version
python --version

# We need to install the postgresql adapter for python,
# But it requires pgsql development headers, and pg8000 won't
# meet our needs here.
if [[ $ARA_TEST_PGSQL == 1 ]]; then
    command -v pg_config >/dev/null 2>&1 || { echo >&2 'pg_config is missing in $PATH, please install postgresql development headers.'; exit 1; }
    pip install psycopg2
fi

# Setup ARA
export ANSIBLE_CALLBACK_PLUGINS="ara/plugins/callbacks"
export ANSIBLE_ACTION_PLUGINS="ara/plugins/actions"
export ANSIBLE_LIBRARY="ara/plugins/modules"
export ARA_DATABASE="${DATABASE}"

# Run linters
bash tests/ansible-linters.sh

# Run test playbooks
# smoke.yml run output will be re-used later
ansible-playbook -vv ara/tests/integration/smoke.yml | tee ${LOGDIR}/smoke.yml.txt
ansible-playbook -vv ara/tests/integration/hosts.yml

# This playbook is meant to fail
ansible-playbook -vv ara/tests/integration/failed.yml || true
# This playbook is meant to be interrupted
ansible-playbook -vv ara/tests/integration/incomplete.yml &
sleep 5
kill $!

# Test include role which is a bit special
ansible-playbook -vv ara/tests/integration/include_role.yml

# Run test commands
pbid=$(ara playbook list | awk '/smoke.yml/ {print $2}')

ara playbook show $pbid -f json
ara host list -b $pbid -f yaml
ara host show -b $pbid localhost
ara host facts -b $pbid localhost
ara data list -b $pbid -f csv
ara data show -b $pbid foo
ara play show $(ara play list -a -c ID -f value |head -n1)
ara result show $(ara result list -a -c ID -f value |tail -n1) --long
ara stats show $(ara stats list -c ID -f value |head -n1)
ara task show $(ara task list -a -c ID -f value |head -n1)
ara file list -b $pbid
ara file show $(ara file list -b $pbid -c ID -f value|head -n1)

# Test adhoc ara_record and ara_read
ansible localhost -m ara_record -a "playbook=${pbid} key=output value={{ lookup('file', '${LOGDIR}/smoke.yml.txt') }}"
ansible localhost -m ara_read -a "playbook=${pbid} key=output"

# We want to test pagination in html generation
export ARA_PLAYBOOK_PER_PAGE=3
export ARA_RESULT_PER_PAGE=20
ara generate html ${LOGDIR}/build
ara generate html ${LOGDIR}/build-playbook --playbook $pbid

ara generate junit ${LOGDIR}/junit.xml
ara generate junit ${LOGDIR}/junit-playbook.xml --playbook $pbid
ara generate junit -
python ara/tests/integration/helpers/junit_check.py ${LOGDIR}/junit.xml

ara generate subunit ${LOGDIR}/results.subunit
ara generate subunit ${LOGDIR}/results-playbook.subunit --playbook $pbid
ara generate subunit - > ${LOGDIR}/results-stdout.subunit
subunit2pyunit ${LOGDIR}/results.subunit 2>&1 | cat > ${LOGDIR}/subunit2pyunit.txt

# It's important that ARA behaves well when gzipped
gzip --best --recursive ${LOGDIR}/build

echo "Run complete, logs and build available in ${LOGDIR}"
popd
