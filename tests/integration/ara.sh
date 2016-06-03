#!/bin/bash
set -ex
# This script runs ara-specific integration tests.
# It can be run by itself but is expected to be run from tox -e integration

# Setup ARA
export ANSIBLE_CALLBACK_PLUGINS=${ANSIBLE_CALLBACK_PLUGINS:-/usr/lib/python2.7/site-packages/ara/callback:$VIRTUAL_ENV/lib/python2.7/site-packages/ara/callback:/usr/local/lib/python2.7/dist-packages/ara/callback}

# All integration test data should be kept in ara/tests/integration/
SCRIPT_CWD="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BUILD_DIR="${SCRIPT_CWD}/build"
DATABASE="${SCRIPT_CWD}/ansible.sqlite"
export ARA_DATABASE="sqlite:///${DATABASE}"

# Cleanup previous run
rm -rf $DATABASE
rm -rf $BUILD_DIR

# Run test playbook
ansible-playbook -vv ${SCRIPT_CWD}/playbook.yml

# Run test commands
ara host show $(ara host list -c ID -f value |head -n1)
ara host facts $(ara host list -c ID -f value |head -n1)
ara play show $(ara play list -a -c ID -f value |head -n1)
ara playbook show $(ara playbook list -c ID -f value |head -n1)
ara result show $(ara result list -a -c ID -f value |tail -n1) --long
ara stats show $(ara stats list -c ID -f value |head -n1)
ara task show $(ara task list -a -c ID -f value |head -n1)
ara generate ${BUILD_DIR} && tree ${BUILD_DIR}
