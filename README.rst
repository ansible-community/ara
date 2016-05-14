ARA: Ansible Run Analysis
=========================
tl;dr
-----
ARA_ is an attempt to make Ansible_ runs easier to visualize, understand and
troubleshoot.

ARA is three things:

1. An `Ansible callback plugin`_ to record playbook runs into a database
2. A `CLI client`_ to query the database
3. A `web interface`_ to visualize the database

.. _ARA: https://github.com/dmsimard/ara
.. _Ansible: https://www.ansible.com/
.. _Ansible callback plugin: https://ara.readthedocs.io/en/latest/configuration.html#ansible
.. _CLI client: https://ara.readthedocs.io/en/latest/usage.html#querying-the-database-with-the-cli
.. _web interface: https://ara.readthedocs.io/en/latest/usage.html#browsing-the-web-interface

What does the web interface look like ?
---------------------------------------
A video is available on YouTube_ and the following is a screenshot of the
web interface:

.. image:: docs/images/preview.png

.. _YouTube: https://www.youtube.com/watch?v=K3jTqgm2YuY

Documentation
-------------
Documentation is available on `readthedocs.io`_.

.. _readthedocs.io: https://ara.readthedocs.io/en/latest/

Installing and Using ARA
------------------------
Please refer to the documentation to install_, configure_ and use_ ARA.

.. _install: https://ara.readthedocs.io/en/latest/installation.html
.. _configure: https://ara.readthedocs.io/en/latest/configuration.html
.. _use: https://ara.readthedocs.io/en/latest/usage.html

Author
======
David Moreau Simard

Contributors and special thanks
===============================
See contributors on GitHub_.

Special thanks to `Lars Kellogg-Stedman`_ for the early feedback on the
project, ideas and code contributions.

.. _GitHub: https://github.com/dmsimard/ara/graphs/contributors
.. _Lars Kellogg-Stedman: http://blog.oddbit.com/

Copyright
=========
Copyright 2016 Red Hat, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
