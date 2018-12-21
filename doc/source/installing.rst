.. _installing:

Installing ara-server
=====================

``ara-server`` requires a Linux distribution with python 3 in order to work.

It is recommended to use a python `virtual environment <https://docs.python.org/3/tutorial/venv.html>`_
in order to avoid conflicts with your Linux distribution python packages::

    # Create a virtual environment
    python3 -m venv ~/.ara/venv

    # Install ara-server from source
    ~/.ara/venv/bin/pip install git+https://git.openstack.org/openstack/ara-server

    # or install it from PyPi
    ~/.ara/venv/bin/pip install ara-server
