.. _ara_api_lookup:

Querying ARA from inside playbooks
==================================

ara_api
-------

ARA comes with a built-in Ansible lookup plugin called ``ara_api`` that can be
made available by :ref:`configuring Ansible <ansible-configuration>` with the
``ANSIBLE_LOOKUP_PLUGINS`` environment variable or the ``lookup_plugins``
setting in an ``ansible.cfg`` file.

There is no other configuration required for this lookup plugin to work since
it retrieves necessary settings (such as API server endpoint and authentication)
from the callback plugin.

The ``ara_api`` lookup plugin can be used to do free-form queries to the
ARA API while the playbook is running:

.. code-block:: yaml

    - name: Test playbook
      hosts: localhost
      tasks:
        - name: Get list of playbooks
          set_fact:
            playbooks: "{{ lookup('ara_api', '/api/v1/playbooks') }}"

ara_playbook
------------

The ``ara_playbook`` Ansible action plugin can be enabled by
:ref:`configuring Ansible <ansible-configuration>` with the
``ANSIBLE_ACTION_PLUGINS`` environment variable or the ``action_plugins``
setting in an ``ansible.cfg`` file.

There is no other configuration required for this action plugin to work since
it retrieves necessary settings (such as API server endpoint and authentication)
from the callback plugin.

The ``ara_playbook`` action plugin can be used in combination with ``ara_api``
to query the API about the current playbook:

.. code-block:: yaml

    - name: Test playbook
      hosts: localhost
      tasks:
        - name: Get the currently running playbook
          ara_playbook:
          register: playbook_query

        - name: Get failed tasks for the currently running playbook
          vars:
            playbook_id: "{{ playbook_query.playbook.id | string }}"
          set_fact:
            tasks: "{{ lookup('ara_api', '/api/v1/tasks?status=failed&playbook=' + playbook_id) }}"
