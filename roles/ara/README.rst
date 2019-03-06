ansible-role-ara
================

This Ansible role provides a framework for installing one or many instances of
`ara <https://github.com/openstack/ara>`_ in a variety of opinionated
deployment topologies.

It is currently tested and supported against Ubuntu 18.04 and Fedora 29.

Role Variables
--------------

See `defaults/main.yaml <https://github.com/openstack/ara/blob/feature/1.0/roles/ara/defaults/main.yaml>`_.

TL;DR
-----

Playbook that runs the role with defaults::

    # Doesn't require superuser privileges
    # The API will only be reachable by the offline API client
    - name: Install ARA with default settings and no persistent API server
      hosts: all
      gather_facts: yes
      vars:
        ansible_python_interpreter: /usr/bin/python3
      roles:
        - ara

What the role ends up doing by default:

- Installs required packages (``git``, ``virtualenv``, etc.) if superuser privileges are available
- Stores everything in the home directory of the user in ``~/.ara``
- Retrieves ARA from source
- Installs ARA in a virtualenv
- Generates a random secret key if none are already configured or provided
- Sets up API configuration in ``~/.ara/server/settings.yaml``
- Runs the API SQL migrations (``ara-manage migrate``)
- Collects static files (``ara-manage collectstatic``) into ``~/.ara/www``

About deployment topologies
---------------------------

This Ansible role is designed to support different opinionated topologies that
can be selected with role variables.

For example, the following role variables are used to provide the topology from
the ``TL;DR`` above:

- ``ara_install_method: source``
- ``ara_wsgi_server: null``
- ``ara_database_engine: django.db.backends.sqlite3``
- ``ara_web_server: null``

The intent is that as the role gains support for other install methods,
wsgi servers, database engines or web servers, it will be possible to
mix and match according to preference or requirements.

Perhaps ARA could be installed from pypi and run with uwsgi, nginx and mysql.
Or maybe it could be installed from distribution packages and set up to run
with apache, mod_wsgi and postgresql.
Or any combination of any of those.

Example playbooks
-----------------

Install ARA and set up the API to be served by a persistent gunicorn service::

    # Requires superuser privileges to set up the ara-api service
    # The API will be reachable at http://127.0.0.1:8000/api/v1/
    - name: Install ARA and set up the API to be served by gunicorn
      hosts: all
      gather_facts: yes
      vars:
        ansible_python_interpreter: /usr/bin/python3
        ara_wsgi_server: gunicorn
      roles:
        - ara

Install ARA and set up the API to be served by nginx in front of gunicorn::

    # Requires superuser privileges to set up nginx and the ara-api service
    # The API will be reachable at http://api.ara.example.org
    - name: Install ARA and set up the API to be served by nginx in front of gunicorn
      hosts: all
      gather_facts: yes
      vars:
        ansible_python_interpreter: /usr/bin/python3
        ara_web_server: nginx
        ara_wsgi_server: gunicorn
        ara_www_dir: /var/www/ara
        ara_api_fqdn: api.ara.example.org
        ara_allowed_hosts:
          - api.ara.example.org
      roles:
        - ara

Copyright
---------

::

    Copyright (c) 2019 Red Hat, Inc.

    ARA Records Ansible is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ARA Records Ansible is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with ARA Records Ansible. If not, see <http://www.gnu.org/licenses/>.
