.. installation:

Installing ARA
==============

Requirements and dependencies
-----------------------------

ARA should work on any Linux distributions as long as python3 is available.

Since ARA provides Ansible plugins to record data, it should be installed
wherever Ansible is running from so that Ansible can use those plugins.
The API server does not require to run on the same machine as Ansible.

By default, only the client and plugin dependencies are installed.
This lets users record and send data to a remote API server without requiring
that the API server dependencies are installed.

If you are standing up an API server or if your use case is about recording
data locally or offline, the required dependencies can be installed
automatically by suffixing ``[server]`` to your pip install commands.

Installing from PyPi or from source
-----------------------------------

First, it is recommended to use a python `virtual environment <https://docs.python.org/3/tutorial/venv.html>`_
in order to avoid conflicts with your Linux distribution python packages.

.. code-block:: bash

    python3 -m venv ~/.ara/virtualenv

To install the latest pre-release for ARA 1.0 from PyPi_:

.. code-block:: bash

    # With the API server dependencies
    ~/.ara/virtualenv/bin/pip install --pre ara[server]

    # Without the API server dependencies
    ~/.ara/virtualenv/bin/pip install --pre ara

Installing from source is possible by using the
`feature/1.0 <https://github.com/ansible-community/ara@feature/1.0>`_ branch:

.. code-block:: bash

    # With the API server dependencies
    ~/.ara/virtualenv/bin/pip install git+https://github.com/ansible-community/ara@feature/1.0[server]

    # Without the API server dependencies
    ~/.ara/virtualenv/bin/pip install git+https://github.com/ansible-community/ara@feature/1.0

.. _PyPi: https://pypi.org/project/ara/

With Ansible roles
------------------

Two roles are built-in to help users configure their API and web deployments:

- :ref:`ansible-role-ara-api` to install the python parts (Ansible plugins, API server)
- :ref:`ansible-role-ara-web` to install the web client (nodejs, react+patternfly)
