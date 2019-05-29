.. _ara_record:

Recording arbitrary data in playbooks
=====================================

ARA comes with a built-in Ansible action plugin called ``ara_record``.

This module can be used as an action for a task in your Ansible playbooks in
order to register whatever you'd like in a key/value format, for example:

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
            msg: "{{ version.playbook_id }} - {{ version.key }}: {{ version.value }}

It also supports different types of data which will have an impact on how a
value might later be parsed or displayed:

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

Recording data for playbooks after completion
---------------------------------------------

It is possible to run an ``ara_record`` task on a specific playbook that might
already be completed by specifying a playbook. This is particularly useful for
recording data that might only be available or computed after your playbook run
has been completed:

.. code-block:: yaml

    ---
    # Write data to a specific (previously run) playbook
    - ara_record:
        playbook: 14
        key: logs
        value: "{{ lookup('file', '/var/log/ansible.log') }}"
        type: text

Or as an ad-hoc command:

.. code-block:: bash

    ansible localhost -m ara_record \
            -a "playbook=14 key=logs value={{ lookup('file', '/var/log/ansible.log') }}"

This data will be recorded inside ARA's database and associated with the
particular playbook run that was executed.

These records can later be retrieved through the API or through a web interface.
