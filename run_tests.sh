#!/bin/bash
# Runs ARA tests
tox -e pep8
tox -e py27
tox -e integration
