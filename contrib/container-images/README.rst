Running ARA API server container images
=======================================

The ARA API server is a good candidate for being served out of a container as
the configuration and state can be kept in persistent files and databases.

The project maintains `different scripts <https://github.com/ansible-community/ara/tree/master/contrib/container-images>`_
that are used to build and push simple container images to
`DockerHub <https://hub.docker.com/repository/docker/recordsansible/ara-api>`_.

The scripts are designed to yield images that are opinionated and
"batteries-included" for the sake of simplicity.
They install the necessary packages for connecting to MySQL and PostgreSQL
databases and set up gunicorn as the application server.

You are encouraged to use these scripts as a base example that you can build,
tweak and improve the container image according to your specific needs and
preferences.

For example, precious megabytes can be saved by installing only the things you
need and you can change the application server as well as it's configuration.

Building an image with buildah
------------------------------

You will need to install `buildah <https://github.com/containers/buildah/blob/master/install.md>`_.

The different scripts to build container images are available in the git repository:

- fedora-distribution.sh_: Builds an image from Fedora 41 `distribution packages <https://koji.fedoraproject.org/koji/packageinfo?packageID=24394>`_
- fedora-pypi.sh_: Builds an image from `PyPi <https://pypi.org/project/ara>`_ packages on Fedora 41
- fedora-source.sh_: Builds an image from `git source <https://github.com/ansible-community/ara>`_ on Fedora 41
- centos-pypi.sh_: Builds an image from `PyPi <https://pypi.org/project/ara>`_ packages on CentOS 9 Stream
- centos-source.sh_: Builds an image from `git source <https://github.com/ansible-community/ara>`_ on CentOS 9 Stream

.. _fedora-distribution.sh: https://github.com/ansible-community/ara/blob/master/contrib/container-images/fedora-distribution.sh
.. _fedora-pypi.sh: https://github.com/ansible-community/ara/blob/master/contrib/container-images/fedora-pypi.sh
.. _fedora-source.sh: https://github.com/ansible-community/ara/blob/master/contrib/container-images/fedora-source.sh
.. _centos-pypi.sh: https://github.com/ansible-community/ara/blob/master/contrib/container-images/centos-pypi.sh
.. _centos-source.sh: https://github.com/ansible-community/ara/blob/master/contrib/container-images/centos-source.sh

The scripts have no arguments other than the ability to specify an optional name
and tag:

.. code-block:: bash

    $ git clone https://github.com/ansible-community/ara
    $ cd ara/contrib/container-images
    $ ./fedora-source.sh ara-api:latest
    # [...]
    Getting image source signatures
    Copying blob 59bbb69efd73 skipped: already exists
    Copying blob ccc3e7c17eae done
    Copying config fb679fc301 done
    Writing manifest to image destination
    Storing signatures
    fb679fc301dde7007b4d219f1d30060b3b4b0d5883b030ee7058d7e9f5969fbe

The image will be available for use once the script has finished running:

.. code-block:: bash

    $ buildah images
    REPOSITORY          TAG      IMAGE ID       CREATED          SIZE
    localhost/ara-api   latest   fb679fc301dd   25 minutes ago   451 MB

Running an image with podman
----------------------------

You will need to install `podman <https://podman.io/getting-started/installation>`_.

Once an image has been built with the scripts above, you can validate that it
is available to podman:

.. code-block:: bash

    $ podman images
    REPOSITORY          TAG      IMAGE ID       CREATED          SIZE
    localhost/ara-api   latest   fb679fc301dd   31 minutes ago   451 MB

First, create a directory where settings, logs and sqlite databases will
persist inside a volume and then start the container:

.. code-block:: bash

    $ mkdir -p ~/.ara/server
    $ podman run --name ara-api --detach --tty \
         --volume ~/.ara/server:/opt/ara:z -p 8000:8000 \
         localhost/ara-api
    bc4b7630c265bdac161f2e08116f3f45c2db519fb757ddf865bb0f212780fa8d

You can validate if the container is running properly with podman:

.. code-block:: bash

    $ podman ps
    CONTAINER ID  IMAGE                     COMMAND               CREATED         STATUS             PORTS                   NAMES
    bc4b7630c265  localhost/ara-api:latest  /usr/bin/gunicorn...  12 seconds ago  Up 11 seconds ago  0.0.0.0:8000->8000/tcp  ara-api

    $ podman logs ara-api
    [ara] No setting found for SECRET_KEY. Generating a random key...
    [ara] Writing default settings to /opt/ara/settings.yaml
    [ara] Using settings file: /opt/ara/settings.yaml
    Operations to perform:
    Apply all migrations: admin, api, auth, contenttypes, db, sessions
    Running migrations:
    Applying contenttypes.0001_initial... OK
    Applying auth.0001_initial... OK
    Applying admin.0001_initial... OK
    Applying admin.0002_logentry_remove_auto_add... OK
    Applying admin.0003_logentry_add_action_flag_choices... OK
    Applying api.0001_initial... OK
    Applying api.0002_remove_host_alias... OK
    Applying api.0003_add_missing_result_properties... OK
    Applying api.0004_duration_in_database... OK
    Applying api.0005_unique_label_names... OK
    Applying contenttypes.0002_remove_content_type_name... OK
    Applying auth.0002_alter_permission_name_max_length... OK
    Applying auth.0003_alter_user_email_max_length... OK
    Applying auth.0004_alter_user_username_opts... OK
    Applying auth.0005_alter_user_last_login_null... OK
    Applying auth.0006_require_contenttypes_0002... OK
    Applying auth.0007_alter_validators_add_error_messages... OK
    Applying auth.0008_alter_user_username_max_length... OK
    Applying auth.0009_alter_user_last_name_max_length... OK
    Applying auth.0010_alter_group_name_max_length... OK
    Applying auth.0011_update_proxy_permissions... OK
    Applying db.0001_initial... OK
    Applying sessions.0001_initial... OK
    [2020-05-05 17:29:22 +0000] [1] [INFO] Starting gunicorn 20.0.4
    [2020-05-05 17:29:22 +0000] [1] [INFO] Listening at: http://0.0.0.0:8000 (1)
    [2020-05-05 17:29:22 +0000] [1] [INFO] Using worker: sync
    [2020-05-05 17:29:22 +0000] [5] [INFO] Booting worker with pid: 5
    [2020-05-05 17:29:22 +0000] [6] [INFO] Booting worker with pid: 6
    [2020-05-05 17:29:23 +0000] [7] [INFO] Booting worker with pid: 7
    [2020-05-05 17:29:23 +0000] [8] [INFO] Booting worker with pid: 8

At this point, the API server will be running but it'll be empty.

Data must be sent to it by running an Ansible playbook with the ARA callback
installed and configured to use this API server.

Sending data to the API server
------------------------------

Here's an example of how it works:

.. code-block:: bash

    # Create and source a python3 virtual environment
    python3 -m venv ~/.ara/virtualenv
    source ~/.ara/virtualenv/bin/activate

    # Install Ansible and ARA
    pip3 install ansible ara

    # Configure Ansible to know where ARA's callback plugin is located
    export ANSIBLE_CALLBACK_PLUGINS=$(python3 -m ara.setup.callback_plugins)

    # Set up the ARA callback to know where the API server is
    export ARA_API_CLIENT=http
    export ARA_API_SERVER="http://127.0.0.1:8000"

    # Run any of your Ansible playbooks as you normally would
    ansible-playbook playbook.yml

As each task from the playbook starts and completes, their data will be
available on the API server in real time as you refresh your queries.

Common operations
-----------------

Modifying ARA's API server settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Settings for the API server will be found in ``~/.ara/server/settings.yaml``
(or ``/opt/ara/settings.yaml`` inside the container) and modifications are
effective after a container restart:

.. code-block:: bash

    podman restart ara-api

See the `documentation <https://ara.readthedocs.io/en/latest/api-configuration.html>`_
for the full list of available options.

Running outside of localhost
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To run an API server that can be queried from other hosts, edit
``~/.ara/server/settings.yaml`` and add the desired hostname (or IP) in
`ALLOWED_HOSTS <https://ara.readthedocs.io/en/latest/api-configuration.html#ara-allowed-hosts>`_.

Connecting to mysql, mariadb or postgresql backends
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ARA API server is a good candidate for living in a container because the
state can be stored on remote database servers.

To connect to database backends other than the sqlite default, edit
``~/.ara/server/settings.yaml`` and look for the following settings:

- `DATABASE_ENGINE <https://ara.readthedocs.io/en/latest/api-configuration.html#ara-database-engine>`_
- `DATABASE_NAME <https://ara.readthedocs.io/en/latest/api-configuration.html#ara-database-name>`_
- `DATABASE_USER <https://ara.readthedocs.io/en/latest/api-configuration.html#ara-database-user>`_
- `DATABASE_PASSWORD <https://ara.readthedocs.io/en/latest/api-configuration.html#ara-database-password>`_
- `DATABASE_HOST <https://ara.readthedocs.io/en/latest/api-configuration.html#ara-database-host>`_
- `DATABASE_PORT <https://ara.readthedocs.io/en/latest/api-configuration.html#ara-database-port>`_
- `DATABASE_CONN_MAX_AGE <https://ara.readthedocs.io/en/latest/api-configuration.html#ara-database-conn-max-age>`_

Running SQL migrations
~~~~~~~~~~~~~~~~~~~~~~

The container image will automatically take care of running SQL migrations before
starting.

However, if you need to run them manually, either for a new database or after
an upgrade, the command ``ara-manage migrate`` can be run from inside the container:

.. code-block:: bash

    $ podman exec -it ara-api ara-manage migrate
    [ara] Using settings file: /opt/ara/settings.yaml
    Operations to perform:
    Apply all migrations: admin, api, auth, contenttypes, db, sessions
    Running migrations:
    Applying contenttypes.0001_initial... OK
    Applying auth.0001_initial... OK
    Applying admin.0001_initial... OK
    Applying admin.0002_logentry_remove_auto_add... OK
    Applying admin.0003_logentry_add_action_flag_choices... OK
    Applying api.0001_initial... OK
    Applying api.0002_remove_host_alias... OK
    Applying api.0003_add_missing_result_properties... OK
    Applying api.0004_duration_in_database... OK
    Applying api.0005_unique_label_names... OK
    Applying contenttypes.0002_remove_content_type_name... OK
    Applying auth.0002_alter_permission_name_max_length... OK
    Applying auth.0003_alter_user_email_max_length... OK
    Applying auth.0004_alter_user_username_opts... OK
    Applying auth.0005_alter_user_last_login_null... OK
    Applying auth.0006_require_contenttypes_0002... OK
    Applying auth.0007_alter_validators_add_error_messages... OK
    Applying auth.0008_alter_user_username_max_length... OK
    Applying auth.0009_alter_user_last_name_max_length... OK
    Applying auth.0010_alter_group_name_max_length... OK
    Applying auth.0011_update_proxy_permissions... OK
    Applying db.0001_initial... OK
    Applying sessions.0001_initial... OK
