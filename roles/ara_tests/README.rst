ansible-role-ara-tests
======================

An Ansible role that installs ARA and Ansible to run quick and inexpensive
tests that do not require superuser privileges.

Role Variables
--------------

See `defaults/main.yaml <https://github.com/ansible-community/ara/blob/feature/1.0/roles/ara_tests/defaults/main.yaml>`_.

.. literalinclude:: ../../roles/ara_tests/defaults/main.yaml
   :language: yaml+jinja
   :start-after: www.gnu.org

TL;DR
-----

.. code-block:: yaml+jinja

   - name: Test ARA with the latest version of Ansible
     hosts: all
     gather_facts: yes
     roles:
       - ara_tests

What the role ends up doing by default:

- Creates a directory to contain the files for the duration of the tests
- Installs ARA from source and the latest version of Ansible in a virtualenv
- Runs test playbooks designed to exercise different features of ARA

.. _include_delimiter_end:

Copyright
---------

.. code-block:: text

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
   along with ARA Records Ansible. If not, see <http://www.gnu.org/licenses/>.
