#!/bin/bash
# This script runs ansible-specific integration tests with ARA configured.
# It can be run by itself but is expected to be run from tox -e integration.
function integration_warning {
    echo "###################### !!!!!!! WARNING !!!!!!! ######################"
    echo "This script will run Ansible destructive integration tests."
    echo "- https://github.com/ansible/ansible/tree/devel/test/integration"
    echo "It will write files, install packages and modify configuration."
    echo "You should really only run this on virtual or ephemeral environments."
    echo "###################### !!!!!!! WARNING !!!!!!! ######################"
    read -p "Are you sure you want to proceed ? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborting execution"
        exit 1
    fi
}

DESTRUCTIVE_TESTS=${DESTRUCTIVE_TESTS:-"false"}
[[ "${DESTRUCTIVE_TESTS}" == "false" ]] && integration_warning

set -ex
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
rm -rf ansible

# Setup and run Ansible destructive integration tests
# Note: Assumes pip and the packages in other-requirements.txt have been installed
TAG=${1:-v2.0.1.0-1}
git clone https://github.com/ansible/ansible
pushd ansible
git checkout ${TAG}
cd test/integration
make destructive
popd

# Run test commands
ara host show $(ara host list -c ID -f value |head -n1)
ara host facts $(ara host list -c ID -f value |head -n1)
ara play show $(ara play list -a -c ID -f value |head -n1)
ara playbook show $(ara playbook list -c ID -f value |head -n1)
ara result show $(ara result list -a -c ID -f value |tail -n1) --long
ara stats show $(ara stats list -c ID -f value |head -n1)
ara task show $(ara task list -a -c ID -f value |head -n1)
ara generate ${BUILD_DIR} && tree ${BUILD_DIR}
