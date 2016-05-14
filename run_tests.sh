#!/bin/bash
# Runs ARA tests
tox -e pep8
tox -e integration
