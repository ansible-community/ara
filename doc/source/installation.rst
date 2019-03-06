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

Using ansible-role-ara
----------------------

An Ansible role is available to install and configure ARA.

For more details, refer to the role documentation: :ref:`ansible-role-ara`.
