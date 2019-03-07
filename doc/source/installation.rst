.. installation:

Installing ARA
==============

Manually with pip
-----------------

ARA should work on any Linux distributions as long as python3 is available.

It is recommended to use a python `virtual environment <https://docs.python.org/3/tutorial/venv.html>`_
in order to avoid conflicts with your Linux distribution python packages::

    # Create a virtual environment
    python3 -m venv ~/.ara/venv

    # Install ARA 1.0 from source
    ~/.ara/venv/bin/pip install git+https://git.openstack.org/openstack/ara@feature/1.0

Using Ansible roles
-------------------

Two roles are built-in to help users configure their API and web deployments:

- :ref:`ansible-role-ara-api` to install the python parts (Ansible plugins, API server)
- :ref:`ansible-role-ara-web` to install the web client (nodejs, react+patternfly)
