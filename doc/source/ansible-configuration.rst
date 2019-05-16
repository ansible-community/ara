Configuring Ansible to use ARA
==============================

To begin using ARA, you'll first need to tell Ansible where it is located.

Since this location will be different depending on your operating system and
how you are installing ARA, there are convenient python modules to help you
figure out the right paths.

Once you've set up the ``callback_plugins`` configuration or the
``ANSIBLE_CALLBACK_PLUGINS`` environment variable, Ansible will automatically
use the ARA callback plugin to start recording data.

If you'd like to use the ``ara_record`` action plugin to record arbitrary data
during your playbook, you'll need to set ``action_plugins`` and
``ANSIBLE_ACTION_PLUGINS`` as well.

Using setup helper modules
--------------------------

The modules can be used directly on the command line:

.. code-block:: bash

    $ python3 -m ara.setup.path
    /usr/lib/python3.7/site-packages/ara

    $ python3 -m ara.setup.plugins
    /usr/lib/python3.7/site-packages/ara/plugins

    $ python3 -m ara.setup.action_plugins
    /usr/lib/python3.7/site-packages/ara/plugins/action

    $ python3 -m ara.setup.callback_plugins
    /usr/lib/python3.7/site-packages/ara/plugins/callback

    # Note: This doesn't export anything, it only prints the commands.
    # If you want to export directly from the command, you can use:
    #     source <(python3 -m ara.setup.env)
    $ python3 -m ara.setup.env
    export ANSIBLE_CALLBACK_PLUGINS=/usr/lib/python3.7/site-packages/ara/plugins/callback
    export ANSIBLE_ACTION_PLUGINS=/usr/lib/python3.7/site-packages/ara/plugins/action

    $ python3 -m ara.setup.ansible
    [defaults]
    callback_plugins=/usr/lib/python3.7/site-packages/ara/plugins/callback
    action_plugins=/usr/lib/python3.7/site-packages/ara/plugins/action

Or from python, for example:

.. code-block:: python

    >>> from ara.setup import callback_plugins
    >>> print(callback_plugins)
    /usr/lib/python3.7/site-packages/ara/plugins/callback

    >>> from ara.setup import action_plugins
    >>> print(action_plugins)
    /usr/lib/python3.7/site-packages/ara/plugins/action
