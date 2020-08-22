.. _ansible-configuration:

Ansible configuration to use ara
================================

In order to be able to use ara :ref:`Ansible plugins <ansible_plugins>`, Ansible must first know where they have been installed.

Since this location will be different depending on the operating system, the version of python or how ara has been
installed, there are convenient python helper modules that provide the right paths:

.. code-block:: bash

    $ python3 -m ara.setup.path
    /usr/lib/python3.7/site-packages/ara

    $ python3 -m ara.setup.plugins
    /usr/lib/python3.7/site-packages/ara/plugins

    $ python3 -m ara.setup.action_plugins
    /usr/lib/python3.7/site-packages/ara/plugins/action
    $ export ANSIBLE_ACTION_PLUGINS=$(python3 -m ara.setup.action_plugins)

    $ python3 -m ara.setup.callback_plugins
    /usr/lib/python3.7/site-packages/ara/plugins/callback
    $ export ANSIBLE_CALLBACK_PLUGINS=$(python3 -m ara.setup.callback_plugins)

    $ python3 -m ara.setup.lookup_plugins
    /usr/lib/python3.7/site-packages/ara/plugins/lookup
    $ export ANSIBLE_LOOKUP_PLUGINS=$(python3 -m ara.setup.lookup_plugins)

    # Note: This doesn't export anything, it only prints the commands.
    # To export directly from the command, use:
    #     source <(python3 -m ara.setup.env)
    $ python3 -m ara.setup.env
    export ANSIBLE_CALLBACK_PLUGINS=/usr/lib/python3.7/site-packages/ara/plugins/callback
    export ANSIBLE_ACTION_PLUGINS=/usr/lib/python3.7/site-packages/ara/plugins/action
    export ANSIBLE_LOOKUP_PLUGINS=/usr/lib/python3.7/site-packages/ara/plugins/lookup

    $ python3 -m ara.setup.ansible
    [defaults]
    callback_plugins=/usr/lib/python3.7/site-packages/ara/plugins/callback
    action_plugins=/usr/lib/python3.7/site-packages/ara/plugins/action
    lookup_plugins=/usr/lib/python3.7/site-packages/ara/plugins/lookup

These helpers are also available directly in python:

.. code-block:: python

    >>> from ara.setup import callback_plugins
    >>> print(callback_plugins)
    /usr/lib/python3.7/site-packages/ara/plugins/callback

    >>> from ara.setup import action_plugins
    >>> print(action_plugins)
    /usr/lib/python3.7/site-packages/ara/plugins/action

    >>> from ara.setup import lookup_plugins
    >>> print(lookup_plugins)
    /usr/lib/python3.7/site-packages/ara/plugins/lookup
