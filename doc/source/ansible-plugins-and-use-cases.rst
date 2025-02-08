.. _ansible_plugins:

Ansible plugins and use cases
=============================

ara_default callback: recording playbooks from Ansible
------------------------------------------------------

The ``ara_default`` Ansible callback plugin can be enabled by :ref:`configuring Ansible <ansible-configuration>` with the
``ANSIBLE_CALLBACK_PLUGINS`` environment variable or the ``callback_plugins`` setting in an ``ansible.cfg`` file.

The callback is the component that recovers data during playbook execution and sends it to the API.

By default, the callback is configured up to use the local API server with the offline API client but it can be set up
to use a remote API server, authenticate with credentials and more:

.. literalinclude:: ../../ara/plugins/callback/ara_default.py
  :language: yaml
  :start-after: DOCUMENTATION
  :end-before: """

For example, a customized callback plugin configuration might look like this in an ``ansible.cfg`` file:

.. code-block:: ini

    [ara]
    api_client = http
    api_server = https://demo.recordsansible.org
    api_username = user
    api_password = password
    api_timeout = 15
    callback_threads = 4
    argument_labels = check,tags,subset
    default_labels = prod,deploy
    ignored_facts = all
    ignored_files = .ansible/tmp,vault.yaml,vault.yml
    ignored_arguments = extra_vars,vault_password_files
    localhost_as_hostname = true
    localhost_as_hostname_format = fqdn

or as environment variables:

.. code-block:: bash

    export ARA_API_CLIENT=http
    export ARA_API_SERVER="https://demo.recordsansible.org"
    export ARA_API_USERNAME=user
    export ARA_API_PASSWORD=password
    export ARA_API_TIMEOUT=15
    export ARA_CALLBACK_THREADS=4
    export ARA_ARGUMENT_LABELS=check,tags,subset
    export ARA_DEFAULT_LABELS=prod,deploy
    export ARA_IGNORED_FACTS=all
    export ARA_IGNORED_FILES=.ansible/tmp,vault.yaml,vault.yml
    export ARA_IGNORED_ARGUMENTS=extra_vars,vault_password_files
    export ARA_LOCALHOST_AS_HOSTNAME=true
    export ARA_LOCALHOST_AS_HOSTNAME_FORMAT=fqdn

Recording ad-hoc commands
~~~~~~~~~~~~~~~~~~~~~~~~~

It is possible to record `ad-hoc commands <https://docs.ansible.com/ansible/latest/user_guide/intro_adhoc.html>`_ in
addition to playbooks since ara 1.4.1 and Ansible 2.9.7.

Ad-hoc command recording can be enabled by setting to ``true`` the ``ANSIBLE_LOAD_CALLBACK_PLUGINS`` environment
variable or ``bin_ansible_callbacks`` in an ``ansible.cfg`` file.

Playbook names and labels
~~~~~~~~~~~~~~~~~~~~~~~~~

Playbooks recorded by the ara callback can be given names or labels in order to make them easier to find and identify later.

They are set as ordinary Ansible variables and are evaluated at the beginning of each play.
They can be provided directly in playbook files:

.. code-block:: yaml

    - name: Deploy prod environment
      hosts: prod
      vars:
        ara_playbook_name: deploy prod
        ara_playbook_labels:
          - deploy
          - prod
      roles:
        - application

or as extra-vars:

.. code-block:: bash

    ansible-playbook -i hosts playbook.yaml \
        -e ara_playbook_name="deploy prod" \
        -e ara_playbook_labels=deploy,prod

Once set, they can be searched for in the UI, the API:

- ``/api/v1/playbooks?name=prod``
- ``/api/v1/playbooks?label=prod``

or the CLI:

- ``ara playbook list --name prod``
- ``ara playbook list --label prod``

Default labels
~~~~~~~~~~~~~~

Default labels will be applied to every playbook recorded by the callback plugin and can be specified with
an ``ansible.cfg`` file:

.. code-block:: ini

    [defaults]
    # ...
    [ara]
    default_labels = deploy,prod

or through the environment variable ``ARA_DEFAULT_LABELS``:

.. code-block:: bash

    export ARA_DEFAULT_LABELS=deploy,prod

CLI argument labels
~~~~~~~~~~~~~~~~~~~

CLI argument labels will automatically apply labels to playbooks when specified CLI arguments are used.

For example, if ``--check`` is used and set up as an argument label, the playbook will be tagged with
``check:True`` if ``--check`` was used or ``check:False`` if it wasn't.

.. note::
   Some CLI arguments are not always named the same as how they are represented by Ansible.
   For example, ``--limit`` is "subset", ``--user`` is "remote_user" but ``--check`` is "check".

Argument labels can be configured through an ``ansible.cfg`` file:

.. code-block:: ini

    [defaults]
    # ...
    [ara]
    argument_labels = check,subset,tags

or through the environment variable ``ARA_ARGUMENT_LABELS``:

.. code-block:: bash

    export ARA_ARGUMENT_LABELS=check,subset,tags

ara_api: free-form API queries
------------------------------

The ``ara_api`` Ansible lookup plugin can be enabled by :ref:`configuring Ansible <ansible-configuration>` with the
``ANSIBLE_LOOKUP_PLUGINS`` environment variable or the ``lookup_plugins`` setting in an ``ansible.cfg`` file.

It can be used to do free-form queries to the ara API while the playbook is running:

.. code-block:: yaml

    - name: Test playbook
      hosts: localhost
      tasks:
        - name: Get failed results
          set_fact:
            failed: "{{ lookup('ara_api', '/api/v1/results?status=failed') }}"

        - name: Print task data from failed results
          vars:
            task_id: "{{ item.task | string }}"
            task: "{{ lookup('ara_api', '/api/v1/tasks/' + task_id ) }}"
            host_id: "{{ item.host | string }}"
            host: "{{ lookup('ara_api', '/api/v1/hosts/' + host_id) }}"
          debug:
            msg: "{{ host.name }} failed | {{ task.name }} ({{ task.path }}:{{ task.lineno }})"
          loop: "{{ failed.results }}"

ara_playbook: get the running playbook or one in specific
---------------------------------------------------------

The ``ara_playbook`` Ansible action plugin can be enabled by :ref:`configuring Ansible <ansible-configuration>` with the
``ANSIBLE_ACTION_PLUGINS`` environment variable or the ``action_plugins`` setting in an ``ansible.cfg`` file.

Without any arguments, it can be used to return data about the playbook from which it is running:

.. code-block:: yaml

    - name: Test playbook
      hosts: localhost
      tasks:
        - name: Get the currently running playbook
          ara_playbook:
          register: query

        - name: Retrieve playbook id
          set_fact:
            playbook_id: "{{ query.playbook.id | string }}"

        # With the playbook id we can create a link to the playbook report
        - name: Recover base url from ara
          set_fact:
            api_base_url: "{{ lookup('ara_api', '/api/') }}"

        - name: Print link to playbook report
          vars:
            ui_base_url: "{{ api_base_url.api[0] | regex_replace('/api/v1/', '') }}"
          debug:
            msg: "{{ ui_base_url }}/playbooks/{{ playbook_id }}.html"

With an argument, it can retrieve data from a specific playbook:

.. code-block:: yaml

    - name: Test playbook
      hosts: localhost
      tasks:
        - name: Get a specific playbook
          ara_playbook:
            playbook: 9001
          register: query

        - name: Print data about the playbook
          debug:
            msg: "Playbook {{ query.playbook.status }} in {{ query.playbook.duration }}"

.. _ara_record:

ara_record: arbitrary key/values in playbook reports
----------------------------------------------------

The ``ara_record`` Ansible action plugin can be enabled by :ref:`configuring Ansible <ansible-configuration>` with the
``ANSIBLE_ACTION_PLUGINS`` environment variable or the ``action_plugins`` setting in an ``ansible.cfg`` file.

It can be used to attach data or metadata to playbook reports so they are available later:

.. code-block:: yaml

    - name: Test playbook
      hosts: localhost
      tasks:
        - name: Get git version of playbooks
          command: git rev-parse HEAD
          register: git_version

        - name: Record git version
          ara_record:
            key: "git_version"
            value: "{{ git_version.stdout }}"
          register: version

        - name: Print recorded data
          debug:
            msg: "{{ version.playbook_id }} - {{ version.key }}: {{ version.value }}"

It is possible to declare a type which can be used to render the data appropriately later:

.. code-block:: yaml

    - name: Record different things
      ara_record:
        key: "{{ item.key }}"
        value: "{{ item.value }}"
        type: "{{ item.type }}"
      loop:
        - { key: "log", value: "error", type: "text" }
        - { key: "website", value: "http://domain.tld", type: "url" }
        - { key: "data", value: '{ "key": "value" }', type: "json" }
        - { key: "somelist", value: ['one', 'two'], type: "list" }
        - { key: "somedict", value: {'key': 'value' }, type: "dict" }

Adding records to playbooks after their completion
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``ara_record`` can attach data to a specific playbook by providing a playbook id.
This can be useful for attaching data that might only be available once a playbook has been completed:

.. code-block:: yaml

    - name: Attach data to a specific playbook
      ara_record:
        playbook: 9001
        key: logs
        value: "{{ lookup('file', '/var/log/ansible.log') }}"
        type: text

Or as an ad-hoc command:

.. code-block:: bash

    ansible localhost -m ara_record \
            -a "playbook=14 key=logs value={{ lookup('file', '/var/log/ansible.log') }}"
