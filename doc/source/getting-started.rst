Getting started
===============

Requirements
------------

- Any recent Linux distribution or Mac OS with python >=3.5 available
- The ara Ansible plugins must be installed for the same python interpreter as Ansible itself

.. note::
    For RHEL 7 and CentOS 7 it is recommended to run the API server in a container due to missing or outdated dependencies.
    See this `issue <https://github.com/ansible-community/ara/issues/99>`_ for more information.

Recording playbooks without an API server
-----------------------------------------

The default API client, ``offline``, requires API server dependencies to be installed but does not need the API server
to be running in order to query or send data.

With defaults and using a local sqlite database:

.. code-block:: bash

    # Install Ansible and ARA (with API server dependencies) for the current user
    python3 -m pip install --user ansible "ara[server]"

    # Configure Ansible to use the ARA callback plugin
    export ANSIBLE_CALLBACK_PLUGINS="$(python3 -m ara.setup.callback_plugins)"

    # Run an Ansible playbook
    ansible-playbook playbook.yaml

    # Use the CLI to see recorded playbooks
    ara playbook list

    # Start the built-in development server to browse recorded results
    ara-manage runserver

Recording playbooks with an API server
--------------------------------------

When running Ansible from multiple servers or locations, data can be aggregated by running the API server as a service
and configuring the ARA Ansible callback plugin to use the ``http`` API client with the API server endpoint.

The API server is a relatively simple django web application written in python that can run with WSGI application
servers such as gunicorn, uwsgi or mod_wsgi.

Alternatively, the API server can also run from a container image such as the one available on
`DockerHub <https://hub.docker.com/r/recordsansible/ara-api>`_:

.. code-block:: bash

    # Create a directory for a volume to store settings and a sqlite database
    mkdir -p ~/.ara/server

    # Start an API server with podman from the image on DockerHub:
    podman run --name api-server --detach --tty \
      --volume ~/.ara/server:/opt/ara:z -p 8000:8000 \
      docker.io/recordsansible/ara-api:latest

    # or with docker:
    docker run --name api-server --detach --tty \
      --volume ~/.ara/server:/opt/ara:z -p 8000:8000 \
      docker.io/recordsansible/ara-api:latest

Once the server is running, Ansible playbook results can be sent to it by configuring the ARA callback plugin:

.. code-block:: bash

    # Install Ansible and ARA (without API server dependencies) for the current user
    python3 -m pip install --user ansible ara

    # Configure Ansible to use the ARA callback plugin
    export ANSIBLE_CALLBACK_PLUGINS="$(python3 -m ara.setup.callback_plugins)"

    # Set up the ARA callback to know where the API server is located
    export ARA_API_CLIENT="http"
    export ARA_API_SERVER="http://127.0.0.1:8000"

    # Run an Ansible playbook
    ansible-playbook playbook.yaml

    # Use the CLI to see recorded playbooks
    ara playbook list

Data will be available on the API server in real time as the playbook progresses and completes.

Read more about how container images are built and how to run them :ref:`here <container-images>`.

Installing from source
----------------------

ara can be installed from source in order to preview and test unreleased features and improvements:

.. code-block:: bash

    # Without the API server dependencies
    pip install --user git+https://github.com/ansible-community/ara

    # With the API server dependencies
    # (Extras suffixes don't work when supplying the direct git URL)
    git clone https://github.com/ansible-community/ara /tmp/ara-src
    pip install --user "/tmp/ara-src[server]"

Installing from distribution packages
-------------------------------------

ara is fully packaged for Fedora_, OpenSUSE_ as well as Debian_.

There is also a package without the API server available on RHEL 8/CentOS 8 EPEL_.
This package contains the Ansible plugins as well as the API clients which are sufficient to query or send data to a
remote API server.

.. _Fedora: https://koji.fedoraproject.org/koji/packageinfo?packageID=24394
.. _OpenSUSE: https://build.opensuse.org/package/show/devel:languages:python/python-ara
.. _Debian: https://tracker.debian.org/pkg/python-ara
.. _EPEL: https://koji.fedoraproject.org/koji/packageinfo?packageID=24394

Installing with Ansible roles
-----------------------------

A collection of Ansible roles for deploying a production-ready ara API server is available on
`Ansible Galaxy <https://galaxy.ansible.com/recordsansible/ara>`_.

For more information as well as documentation, see the collection GitHub repository: https://github.com/ansible-community/ara-collection/
