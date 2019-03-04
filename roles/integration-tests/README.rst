integration-tests
=================

Installs a specified version of ARA and Ansible into a virtual environment
and runs integration tests that do not require superuser privileges.

Requirements
============

Since the role is designed to run without superuser privileges, the following
things should be installed in order to let the role use them:

- git
- python3
- pip
- virtualenv

Variables
=========

From ``defaults/main.yaml``:

Root directory where integration tests will prepare and store data::

    integration_root: "/tmp/ara-integration-tests"

Directory where the virtualenv will be created::

    integration_virtualenv: "{{ integration_root }}/venv"

Directory where ARA_BASE_DIR will be set::

    integration_data: "{{ integration_root }}/data"

Whether the root directory should be cleaned up between runs::

    integration_cleanup: true

Name of the Ansible package. This can be ``ansible`` which will use pip or it
could be something like ``/home/user/git/ansible`` as well as
``git+https://github.com/ansible/ansible``::

    integration_ansible_name: ansible

Version of Ansible from pypi to install::

    integration_ansible_version: latest
