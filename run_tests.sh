#!/bin/bash

# Ensure the script will exit with an error if a test fails
set -e

# Runs ARA tests
tox -e docs
tox -e pep8
tox -e py27
tox -e integration-smoke
# ansible integration tests can be run manually for the time being
# It requires jumping through hoops if we want to run them inside Travis CI
# tox -e integration-ansible
