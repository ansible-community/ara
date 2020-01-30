Configuring the ARA Ansible plugins
===================================

ARA plugins uses the same mechanism and configuration files as Ansible to
retrieve it's configuration. It comes with sane defaults that can be customized
if need be.

The order of priority is the following:

1. Environment variables
2. ``./ansible.cfg`` (*in the current working directory*)
3. ``~/.ansible.cfg`` (*in the home directory*)
4. ``/etc/ansible/ansible.cfg``

When using the ``ansible.cfg`` file, the configuration options must be set
under the ara namespace, like so:

.. code-block:: ini

    [ara]
    variable = value

.. _configuration_callback:

ARA callback plugin
-------------------

The ARA callback plugin is the component that recovers data throughout the
execution of your playbook and sends it to the API.

By default, the callback plugin is set up to use the local API server with the
offline API client but you can also send data to a remote API server, specify
credentials or customize other parameters:

.. literalinclude:: ../../ara/plugins/callback/ara_default.py
  :language: yaml
  :start-after: DOCUMENTATION
  :end-before: """

For example, a customized callback plugin configuration might look like this in
an ``ansible.cfg`` file:

.. code-block:: ini

    [ara]
    api_client = http
    api_server = https://api.demo.recordsansible.org
    api_username = user
    api_password = password
    api_timeout = 15
    default_labels = dev,deploy
    ignored_facts = ansible_env,ansible_all_ipv4_addresses
    ignored_arguments = extra_vars,vault_password_files

or as environment variables:

.. code-block:: bash

    export ARA_API_CLIENT=http
    export ARA_API_SERVER="https://api.demo.recordsansible.org"
    export ARA_API_USERNAME=user
    export ARA_API_PASSWORD=password
    export ARA_API_TIMEOUT=15
    export ARA_DEFAULT_LABELS=dev,deploy
    export ARA_IGNORED_FACTS=ansible_env,ansible_all_ipv4_addresses
    export ARA_IGNORED_ARGUMENTS=extra_vars,vault_password_files

ARA action plugin: ara_record
-----------------------------

The ``ara_record`` action plugin recovers it's configuration from the callback
plugin.

It is therefore not necessary to configure it explicitely other than
enabling Ansible to find it by setting ``action_plugins`` in ``ansible.cfg`` or
the ``ANSIBLE_ACTION_PLUGINS`` environment variable.