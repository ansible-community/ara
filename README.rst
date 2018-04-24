ara-plugins
===========

**This repository does not contain production ready software.**

If you are looking for the latest stable release of ARA Records Ansible, please
refer to the `openstack/ara`_ repository.

.. _openstack/ara: https://github.com/openstack/ara

Documentation
=============

*Work in progress*

**TL;DR**: Using tox is convenient for the time being::

  # Use the source Luke
  git clone https://github.com/openstack/ara-plugins
  cd ara-plugins

  # Install tox
  pip install tox # (or the tox python library from your distro packages)

  # Run actual tests or get coverage
  tox -e pep8
  tox -e cover

  # Build docs
  tox -e docs

Contributors
============

See contributors on GitHub_.

.. _GitHub: https://github.com/openstack/ara-plugins/graphs/contributors

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
