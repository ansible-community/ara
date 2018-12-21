ara-plugins
===========

.. image:: doc/source/_static/ara-with-icon.png

ARA Records Ansible playbook runs and makes the recorded data available and
intuitive for users and systems.

``ara-plugins`` is a component of ARA which provides:

- An Ansible callback plugin to send Ansible execution data to the ARA API
- Ansible modules to interact with ARA

Disclaimer
==========

``ara-plugins`` is not yet stable and will be shipped as part of a coordinated
ARA 1.0 release. It is not currently recommended for production use.

While most of the major work has landed, please keep in mind that we can still
introduce backwards incompatible changes until we ship the first release.

You are free to use this project and in fact, you are more than welcome to
contribute feedback, bug fixes or improvements !

If you are looking for a stable version of ARA, you can find the latest 0.x
version on PyPi_ and the source is available here_.

.. _PyPi: https://pypi.org/project/ara/
.. _here: https://github.com/openstack/ara

Documentation
=============

Documentation is a work in progress.

To install ara-plugins::

    pip install git+https://github.com/openstack/ara-plugins

Ansible must be configured to know about the location of the plugins in order
for them to work.

The location of the plugins will depend on many factors including your version
of python, your Linux distribution or whether it's been installed from source,
from packages or inside a virtual environment.

ara-plugins provides a command to help you locate its plugins: ``python -m ara.plugins``.
This command returns the path of the plugins directory so you don't need to search for it.

The plugin directory location can also be retrieved in python::

    import os
    from ara.plugins import LOCATION as plugins
    # Do something with the location
    callback_plugins = os.path.join(plugins, "callback")
    action_plugins = os.path.join(plugins, "action")

Here's what your Ansible and ARA configuration might look like in an ``ansible.cfg`` file::

    [defaults]
    # Note: This is an example, use "python -m ara.plugins" to determine the real path
    callback_plugins = /usr/lib/python3.6/site-packages/ara/plugins/callback
    action_plugins = /usr/lib/python3.6/site-packages/ara/plugins/action

    [ara]
    api_client = http
    api_timeout = 30
    api_server = http://127.0.0.1:8000

And what the same thing might look like when setting up configuration with environment variables::

    export ANSIBLE_CALLBACK_PLUGINS="$(python -m ara.plugins)/callback"
    export ANSIBLE_ACTION_PLUGINS="$(python -m ara.plugins)/action"
    export ARA_API_CLIENT=http
    export ARA_API_TIMEOUT=30
    export ARA_SERVER=http://127.0.0.1:8000

Contributors
============

See contributors on GitHub_.

.. _GitHub: https://github.com/openstack/ara-plugins/graphs/contributors

Copyright
=========

::

    Copyright (c) 2018 Red Hat, Inc.

    ARA is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ARA is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with ARA.  If not, see <http://www.gnu.org/licenses/>.
