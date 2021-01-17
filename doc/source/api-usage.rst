Using ARA API clients
=====================

When installing ARA, you are provided with a REST API server and two API
clients out of the box:

- ``AraOfflineClient`` can query the API without needing an API server to be running
- ``AraHttpClient`` is meant to query a specified API server over http

ARA Offline API client
~~~~~~~~~~~~~~~~~~~~~~

If your use case doesn't require a remote or persistent API server, the offline
client lets you query the API without needing to start an API server.

In order to use this client, you would instanciate it like this:

.. code-block:: python

    #!/usr/bin/env python3
    # Import the client
    from ara.clients.offline import AraOfflineClient

    # Instanciate the offline client
    client = AraOfflineClient()

Note that, by default, instanciating an offline client will automatically run
SQL migrations.

If you expect the migrations to have already been run when you instanciate
the client, you can disable automatic SQL migrations with by specifying
``run_sql_migrations=False``:

.. code-block:: python

    client = AraOfflineClient(run_sql_migrations=False)

ARA HTTP API client
~~~~~~~~~~~~~~~~~~~

``AraHttpClient`` works with the same interface, methods and behavior as
``AraOfflineClient``.

You can set your client to communicate with a remote ``ara-server`` API by
specifying an endpoint parameter:

.. code-block:: python

    #!/usr/bin/env python3
    # Import the client
    from ara.clients.http import AraHttpClient

    endpoint = "https://demo.recordsansible.org"
    # Instanciate the HTTP client with an endpoint where an API server is listening
    client = AraHttpClient(endpoint=endpoint)

    # SSL verification can be disabled with verify=False
    client = AraHttpClient(endpoint=endpoint, verify=False)

Example API usage
~~~~~~~~~~~~~~~~~

For more details on the API endpoints, see :ref:`api-documentation:API Documentation`.

Otherwise, once you've instanciated your client, you're ready to query the API.

Here's a code example to help you get started:

.. code-block:: python

    #!/usr/bin/env python3
    # Import the client
    from ara.clients.http import AraHttpClient

    # Instanciate the HTTP client with an endpoint where an API server is listening
    client = AraHttpClient(endpoint="https://demo.recordsansible.org")

    # Get a list of failed playbooks
    # /api/v1/playbooks?status=failed
    playbooks = client.get("/api/v1/playbooks", status="failed")

    # If there are any results from our query, get more information about the
    # failure and print something helpful
    template = "{timestamp}: {host} failed '{task}' ({task_file}:{lineno})"

    for playbook in playbooks["results"]:
        # Get failed results for the playbook
        results = client.get("/api/v1/results?playbook=%s" % playbook["id"])

        # For each result, print the task and host information
        for result in results["results"]:
            task = client.get("/api/v1/tasks/%s" % result["task"])
            host = client.get("/api/v1/hosts/%s" % result["host"])

            print(template.format(
                timestamp=result["ended"],
                host=host["name"],
                task=task["name"],
                task_file=task["path"],
                lineno=task["lineno"]
            ))

Running this script would then provide an output that looks like the following::

    2020-04-18T17:16:13.394056Z: aio1_repo_container-0c92f7a2 failed 'repo_server : Install EPEL gpg keys' (/home/zuul/src/opendev.org/openstack/openstack-ansible-repo_server/tasks/repo_install.yml:16)
    2020-04-18T17:14:59.930995Z: aio1_repo_container-0c92f7a2 failed 'repo_server : File and directory setup (root user)' (/home/zuul/src/opendev.org/openstack/openstack-ansible-repo_server/tasks/repo_pre_install.yml:78)
    2020-04-18T17:14:57.909155Z: aio1_repo_container-0c92f7a2 failed 'repo_server : Git service data folder setup' (/home/zuul/src/opendev.org/openstack/openstack-ansible-repo_server/tasks/repo_pre_install.yml:70)
    2020-04-18T17:14:57.342091Z: aio1_repo_container-0c92f7a2 failed 'repo_server : Check if the git folder exists already' (/home/zuul/src/opendev.org/openstack/openstack-ansible-repo_server/tasks/repo_pre_install.yml:65)
    2020-04-18T17:14:56.793499Z: aio1_repo_container-0c92f7a2 failed 'repo_server : Drop repo pre/post command script' (/home/zuul/src/opendev.org/openstack/openstack-ansible-repo_server/tasks/repo_pre_install.yml:53)
    2020-04-18T17:14:54.507660Z: aio1_repo_container-0c92f7a2 failed 'repo_server : File and directory setup (non-root user)' (/home/zuul/src/opendev.org/openstack/openstack-ansible-repo_server/tasks/repo_pre_install.yml:32)
    2020-04-18T17:14:51.281530Z: aio1_repo_container-0c92f7a2 failed 'repo_server : Create the nginx system user' (/home/zuul/src/opendev.org/openstack/openstack-ansible-repo_server/tasks/repo_pre_install.yml:22)
