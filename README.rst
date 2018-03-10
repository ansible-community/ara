ara-django
==========

.. image:: doc/source/_static/screenshot.png

An experiment with Django at the core of the ARA 1.0 backend.
This is not stable or production-ready.

If you are looking for ARA Records Ansible, the Ansible callback plugin and
reporting interface, you will find the repository here_.

We are prototyping outside the main repository due to the vast changes
involved and will merge back as appropriate.

.. _here: https://github.com/openstack/ara

Documentation
=============

*Work in progress*

This is python3 only right now.

**TL;DR**: Using tox is convenient for the time being::

  # Use the source Luke
  git clone https://github.com/dmsimard/ara-django
  cd ara-django

  # Install tox
  pip install tox # (or the tox python library from your distro packages)

  # Run test server -> http://127.0.0.1:8000/api/v1/
  tox -e runserver

  # Create mock data
  source .tox/runserver/bin/activate
  python standalone/mockdata.py

  # Run actual tests or get coverage
  tox -e pep8
  tox -e py35
  tox -e cover

  # Build docs
  tox -e docs

Contributors
============

See contributors on GitHub_.

.. _GitHub: https://github.com/dmsimard/ara-django/graphs/contributors

Copyright
=========

::

    Copyright (c) 2018 Red Hat, Inc.

    ARA is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ARA is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with ARA.  If not, see <http://www.gnu.org/licenses/>.
