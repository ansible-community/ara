ARA Records Ansible
===================

ARA Records Ansible playbooks and makes them easier to understand and troubleshoot.

.. image:: doc/source/_static/ara-with-icon.png

ARA saves playbook results to a local or remote database by using an Ansible
callback plugin and provides an API to integrate this data in tools and interfaces.

This project provides the ARA API as well as the Ansible components.

For the web client interface, see `ara-web <https://github.com/ansible-community/ara-web>`_.

Quickstart
==========

Here's how you can get started from scratch with sane defaults:

.. code-block:: bash

    # Create a python3 virtual environment and activate it so we don't conflict
    # with system or distribution packages
    python3 -m venv ~/.ara/virtualenv
    source ~/.ara/virtualenv/bin/activate

    # Install Ansible, ARA and it's API server dependencies
    pip install ansible ara[server]

    # Tell Ansible to use the ARA callback plugin
    export ANSIBLE_CALLBACK_PLUGINS="$(python -m ara.setup.callback_plugins)"

    # Run your playbook as usual
    ansible-playbook playbook.yml

If nothing went wrong, your playbook data should have been saved in a local
database at ``~/.ara/server/ansible.sqlite``.

You can browse this data through the API by executing ``ara-manage runserver``
and pointing your browser at http://127.0.0.1:8000/.

That's it !

Live demos
==========

You can find live demos deployed by the built-in ara_api_ and ara_web_ Ansible
roles at https://api.demo.recordsansible.org and https://web.demo.recordsansible.org.

.. _ara_api: https://ara.readthedocs.io/en/feature-1.0/ansible-role-ara-api.html
.. _ara_web: https://ara.readthedocs.io/en/feature-1.0/ansible-role-ara-web.html

Documentation
=============

Documentation for installing, configuring, running and using ARA is
available on `readthedocs.io <https://ara.readthedocs.io/en/feature-1.0/>`_.

Community and getting help
==========================

- Bugs, issues and enhancements: https://github.com/ansible-community/ara/issues
- IRC: #ara on `Freenode <https://webchat.freenode.net/?channels=#ara>`_
- Slack: https://arecordsansible.slack.com (`invitation link <https://join.slack.com/t/arecordsansible/shared_invite/enQtMjMxNzI4ODAxMDQxLWU4MmZhZTI4ZjRjOTUwZTM2MzM3MzcwNDU1YzFmNzRlMzI0NTUzNDY1MWJlNThhM2I4ZTViZjUwZTRkNTBiM2I>`_)

- Website and blog: https://ara.recordsansible.org
- Twitter: https://twitter.com/arecordsansible

Contributors
============

See contributors on `GitHub <https://github.com/ansible-community/ara/graphs/contributors>`_.

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