ARA Records Ansible
===================

.. image:: doc/source/_static/ara-with-icon.png

ARA Records Ansible playbook runs and makes the recorded data available and
intuitive for users and systems.

The project provides several distinct components in order to make this happen:

- An API server for sending and querying data relative to playbook execution results
- An API client library for communicating with the API
- An Ansible callback plugin to record events as they happen throughout the execution
- An Ansible action module to associate arbitrary key/values to your playbook reports

Quickstart
==========

Here's how you can get started from scratch with default settings:

.. code-block:: bash

    # Create a virtual environment and activate it so we don't conflict
    # with system or distribution packages
    python3 -m venv ~/.ara/virtualenv
    source ~/.ara/virtualenv/bin/activate

    # Install Ansible, ARA and it's API server dependencies
    pip install ansible git+https://github.com/ansible-community/ara@feature/1.0[server]

    # Tell Ansible to use the ARA callback plugin
    export ANSIBLE_CALLBACK_PLUGINS="$(python -m ara.setup.callback_plugins)"

    # Run your playbook as your normally would
    ansible-playbook playbook.yml

The data will be saved in real time throughout the execution of the Ansible playbook.

What happens behind the scenes is that the ARA Ansible callback plugin used
the built-in API client to send the data to the API which then saved it to a
database located by default at ``~/.ara/server/ansible.sqlite``.

You're now ready to start poking at the API with the built-in
`API clients <https://ara.readthedocs.io/en/feature-1.0/api-usage.html>`_ !

If you'd like to have the ARA web reporting interface, take a look at
`ara-web <https://github.com/ansible-community/ara-web>`_.

Documentation
=============

Documentation for installing, configuring, running and using ara is
available on `readthedocs.io <https://ara.readthedocs.io/en/feature-1.0/>`_.

Community and getting help
==========================

You can chat with the ARA community on Slack and IRC.
The two are transparently bridged with teamchat_ which broadcasts messages from
one platform to the other.

In addition, you can also find ARA on Twitter: `@ARecordsAnsible <https://twitter.com/ARecordsAnsible>`_

**IRC**

- Server: `irc.freenode.net`_
- Channel: #ara

**Slack**

- https://arecordsansible.slack.com
- Join with the `Slack invitation <https://join.slack.com/t/arecordsansible/shared_invite/enQtMjMxNzI4ODAxMDQxLWU4MmZhZTI4ZjRjOTUwZTM2MzM3MzcwNDU1YzFmNzRlMzI0NTUzNDY1MWJlNThhM2I4ZTViZjUwZTRkNTBiM2I>`_

.. _teamchat: https://github.com/dmsimard/teamchat
.. _irc.freenode.net: https://webchat.freenode.net/

Development and testing
=======================

.. code-block:: bash

  # Retrieve the source and check out the 1.0 branch
  git clone https://github.com/ansible-community/ara
  cd ara
  git checkout feature/1.0

  # Install tox from pip or from your distro packages
  pip install tox

  # Run Ansible integration tests with the latest version of Ansible
  tox -e ansible-integration

  # Run integration tests with a specific version of Ansible
  # Note: tox will always use the latest version of Ansible to run the playbook which runs the tests.
  # For example, if the latest version of Ansible is 2.7.9, it will use Ansible 2.7.9
  # to install Ansible==2.6.15 in a virtual environment and 2.6.15 is what will be tested.
  tox -e ansible-integration -- -e ara_tests_ansible_version=2.6.15

  # Run integration tests with Ansible from source
  tox -e ansible-integration -- -e "ara_tests_ansible_name=git+https://github.com/ansible/ansible"

  # Run unit tests
  tox -e py3

  # Run linters (pep8, black, isort)
  tox -e linters

  # Run test server -> http://127.0.0.1:8000/api/v1/
  tox -e runserver

  # Build docs
  tox -e docs

Contributors
============

See contributors on GitHub_.

.. _GitHub: https://github.com/ansible-community/ara/graphs/contributors

Copyright
=========

::

    Copyright (c) 2019 Red Hat, Inc.

    ARA Records Ansible is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ARA Records Ansible is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with ARA Records Ansible.  If not, see <http://www.gnu.org/licenses/>.