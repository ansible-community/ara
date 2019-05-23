Setting playbook names and labels
=================================

ARA provides the ability for users to specify playbook names and labels in
order to better distinguish playbooks run in different environments or purposes.

Names and labels are also searchable by the ARA API, allowing you to find
playbooks matching your query.

Names and labels are set as regular Ansible variables:

- ``ara_playbook_name``
- ``ara_playbook_labels``

These variables can be provided by your Ansible inventory, directly in your
playbook file, as extra-vars or any other way supported by Ansible.

For example, in an inventory:

.. code-block:: ini

    [dev]
    host1
    host2

    [dev:vars]
    ara_playbook_name=deploy-dev
    ara_playbook_labels='["deploy", "dev"]'

In a playbook:

.. code-block:: yaml

    - name: Deploy dev environment
      hosts: dev
      vars:
        ara_playbook_name: deploy-dev
        ara_playbook_labels:
            - deploy
            - dev
      roles:
        - application

Or as extra-vars:

.. code-block:: bash

    ansible-playbook -i hosts playbook.yaml \
        -e ansible_playbook_name=deploy-dev \
        -e ansible_playbook_labels='["deploy", "dev"]'
