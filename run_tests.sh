#!/bin/bash

# Ensure the script will exit with an error if a test fails
set -e

# Runs ARA tests
tox -e pep8
tox -e py27
tox -e integration
tox -e docs
