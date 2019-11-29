Playbook names and labels
=========================

ARA allows users to specify playbook names and labels in order to better
distinguish playbooks run in different environments or for different purposes.

Once your playbooks have names and labels, the API allows you to easily search
for them, for example:

- ``/api/v1/playbooks?name=<playbook_name>``
- ``/api/v1/playbooks?label=<label_name>``

Names and labels are set as regular Ansible variables:

- ``ara_playbook_name``
- ``ara_playbook_labels``

These variables are picked up by ARA at the beginning of a play and can be
provided directly in your playbook file:

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
        -e ara_playbook_name=deploy-dev \
        -e ara_playbook_labels=deploy,dev

Default labels
--------------

If necessary, ARA can be configured to set one or more labels on every recorded
playbook by default.

This can be done either through an ``ansible.cfg`` file like so:

.. code-block:: ini

    [defaults]
    # ...
    [ara]
    default_labels = first_label,second_label

or through the ``ARA_DEFAULT_LABELS`` environment variable:

.. code-block:: bash

    export ARA_DEFAULT_LABELS=first_label,second_label
