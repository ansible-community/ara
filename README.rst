ARA Records Ansible
===================

ARA Records Ansible playbooks and makes them easier to understand and troubleshoot.

.. image:: doc/source/_static/ara-with-icon.png

ARA saves playbook results to a local or remote database by using an Ansible
callback plugin and provides an API to integrate this data in tools and interfaces.

This project provides ARA's Ansible plugins, the REST API server as well as
simple built-in web interfaces to browse the recorded data.

A stateless javascript client interface is provided by a different project,
`ara-web <https://github.com/ansible-community/ara-web>`_.

Quickstart
==========

Here's how you can get started from scratch with sane defaults with python>=3.5:

.. code-block:: bash

    # Install ARA and Ansible for the current user
    python3 -m pip install --user ansible "ara[server]"

    # Tell Ansible to use the ARA callback plugin
    export ANSIBLE_CALLBACK_PLUGINS="$(python3 -m ara.setup.callback_plugins)"

    # Run your playbook
    ansible-playbook playbook.yml

If nothing went wrong, your playbook data should have been saved in a local
database at ``~/.ara/server/ansible.sqlite``.

You can take a look at the recorded data by running ``ara-manage runserver``
and pointing your browser at http://127.0.0.1:8000/.

That's it !

Live demos
==========

You can find live demos deployed by the built-in ara_api_ and ara_web_ Ansible
roles at https://api.demo.recordsansible.org and https://web.demo.recordsansible.org.

.. _ara_api: https://ara.readthedocs.io/en/latest/ansible-role-ara-api.html
.. _ara_web: https://ara.readthedocs.io/en/latest/ansible-role-ara-web.html

Documentation
=============

Documentation for installing, configuring, running and using ARA is
available on `readthedocs.io <https://ara.readthedocs.io>`_.

Community and getting help
==========================

- Bugs, issues and enhancements: https://github.com/ansible-community/ara/issues
- IRC: #ara on `Freenode <https://webchat.freenode.net/?channels=#ara>`_
- Slack: https://arecordsansible.slack.com (`invitation link <https://join.slack.com/t/arecordsansible/shared_invite/enQtMjMxNzI4ODAxMDQxLTU2NTU3YjMwYzRlYmRkZTVjZTFiOWIxNjE5NGRhMDQ3ZTgzZmQyZTY2NzY5YmZmNDA5ZWY4YTY1Y2Y1ODBmNzc>`_)

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