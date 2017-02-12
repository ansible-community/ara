ARA: Ansible Run Analysis
=========================
.. image:: doc/source/_static/ara-with-icon.png

tl;dr
-----
ARA_ records Ansible_ Playbook runs seamlessly to make them easier to
visualize, understand and troubleshoot. It integrates with Ansible wherever you
run it.

ARA provides four things:

1. An `Ansible callback plugin`_ to record playbook runs into a local or remote database
2. The ara_record_ and ara_read_ pair of Ansible modules to record and read persistent data with ARA
3. A `CLI client`_ to query the database
4. A `dynamic, database-driven web interface`_ that can also be `generated and served from static files`_

.. _ARA: https://github.com/openstack/ara
.. _Ansible: https://www.ansible.com/
.. _Ansible callback plugin: https://ara.readthedocs.io/en/latest/configuration.html#ansible
.. _ara_record: http://ara.readthedocs.io/en/latest/usage.html#using-the-ara-record-module
.. _ara_read: http://ara.readthedocs.io/en/latest/usage.html#using-the-ara-read-module
.. _CLI client: https://ara.readthedocs.io/en/latest/usage.html#querying-the-database-with-the-cli
.. _dynamic, database-driven web interface: https://ara.readthedocs.io/en/latest/faq.html#what-does-the-web-interface-look-like
.. _generated and served from static files: https://ara.readthedocs.io/en/latest/usage.html#generating-a-static-version-of-the-web-application

Discussing ARA
--------------
We hang out in **#ara** on freenode IRC. Come chat with developers and users !

Documentation
-------------
`Frequently asked questions`_ and documentation on how to install_, configure_,
use_ or contribute_ to ARA is available on `readthedocs.io`_.

.. _Frequently asked questions: https://ara.readthedocs.io/en/latest/faq.html
.. _install: https://ara.readthedocs.io/en/latest/installation.html
.. _configure: https://ara.readthedocs.io/en/latest/configuration.html
.. _use: https://ara.readthedocs.io/en/latest/usage.html
.. _contribute: https://ara.readthedocs.io/en/latest/contributing.html

.. _readthedocs.io: https://ara.readthedocs.io/en/latest/

Contributors
============
See contributors on GitHub_.

.. _GitHub: https://github.com/openstack/ara/graphs/contributors

Copyright
=========
Copyright 2017 Red Hat, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
