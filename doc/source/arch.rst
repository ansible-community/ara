Architecture and Workflows
==========================

Recording data from Ansible
---------------------------

.. image:: _static/graphs/recording-workflow.png

0. A human (*or a system, script, etc.*) installs ARA and configures Ansible to use the ARA callback
1. A human (*or a system, script, etc.*) executes an ``ansible-playbook`` command
2. Ansible sends hooks for every event to `callback plugins`_ (``v2_playbook_on_start``, ``v2_runner_on_failed``, etc.)
3. The callback plugin, provided by ara-plugins_, organizes the data sent by Ansible and sends it to the API client
4. The API client, provided by ara-clients_, takes care of actually sending the data to the API over HTTP or locally offline through an internal implementation
5. The API server, provided by ara-server_, receives the POST from the client, validates it and sends it to the database model backend
6. The API server sends a response back to the client with the results
7. The API client sends the response back to the callback with the results
8. The callback plugin returns, ending the callback hook
9. Ansible continues running until it is complete (back to step 2)

.. _callback plugins: https://docs.ansible.com/ansible/latest/plugins/callback.html
.. _ara-plugins: https://github.com/openstack/ara-plugins
.. _ara-clients: https://github.com/openstack/ara-clients
.. _ara-server: https://github.com/openstack/ara-server
