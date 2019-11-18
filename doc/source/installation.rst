.. installation:

Installing ARA
==============

ARA is packaged on PyPi_ as well as for Fedora_ and OpenSUSE_.

This documentation covers the two main components in ARA:

- The Ansible plugins
- The API server and the built-in web interface

See :ref:`ansible-configuration` to enable ARA once it's been installed.

Instructions for ara-web, a javascript API client interface, are available in
the project's `README <https://github.com/ansible-community/ara-web>`_.

Requirements and dependencies
-----------------------------

ARA should work on any Linux distribution as long as python3.5 and greater is
available.

In order to record data, ARA provides Ansible plugins that must be installed
wherever Ansible is running from.

The main package only installs the API client and Ansible plugin dependencies.
This lets users record and send data to a remote API server without requiring
that the API server dependencies are installed.

When recording data locally using the offline client, the API server does not
need to be running but the dependencies must be installed.

Installing from PyPi or from source
-----------------------------------

.. note::

    When installing from source or from PyPi, it is highly recommended to set up
    ARA in either:

    - `user-specific python packages <https://packaging.python.org/tutorials/installing-packages/#installing-to-the-user-site>`_ using ``pip install --user``
    - a python `virtual environment <https://docs.python.org/3/tutorial/venv.html>`_ using ``python3 -m venv </path/to/venv>``

    This will prevent conflicts with your Linux distribution's python packages.

To install the latest release of ARA from PyPi_:

.. code-block:: bash

    # Without the API server dependencies
    pip install --user ara

    # With the API server dependencies
    pip install --user "ara[server]"

Installing from source is possible by using the git repository:

.. code-block:: bash

    # Without the API server dependencies
    pip install --user git+https://github.com/ansible-community/ara

    # With the API server dependencies
    # (Suffixes don't work when supplying the direct git URL)
    git clone https://github.com/ansible-community/ara ara-src
    pip install --user "./ara-src[server]"

Installing from Fedora packages
-------------------------------

The install the latest packaged version of ARA for Fedora:

.. code-block:: bash

    # Without the API server dependencies
    dnf install ara

    # With the API server dependencies
    dnf install ara ara-server

Installing with Ansible roles
-----------------------------

Two Ansible roles are available to help users configure their API and web
deployments:

- :ref:`ansible-role-ara-api` to install the python parts (Ansible plugins, API server)
- :ref:`ansible-role-ara-web` to install the web client (nodejs, react+patternfly)

.. _PyPi: https://pypi.org/project/ara/
.. _Fedora: https://koji.fedoraproject.org/koji/packageinfo?packageID=24394
.. _OpenSUSE: https://build.opensuse.org/package/show/devel:languages:python/python-ara
