Using API clients with ara-server
=================================

Once you've :ref:`installed <installing>` ara-server, you need to know how
you're going to use it.

Typically, `ara-server <https://github.com/openstack/ara-server>`_ is consumed
by `ara-clients <https://github.com/openstack/ara-clients>`_ which currently
provides two python clients for the API.

ARA Offline REST API client
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The default client, ``AraOfflineClient``, is meant to be used to query the API
without requiring users to start or host an instance of ``ara-server``.

To use the offline client, first install ``ara-server`` and ``ara-clients``,
for example::

    # Install ara-server and ara-clients
    python3 -m venv ~/.ara/venv
    ~/.ara/venv/bin/pip install ara-server ara-clients

Then you can use it like this::

    #!/usr/bin/env python3
    # Import the client
    from ara.clients.offline import AraOfflineClient

    # Instanciate the offline client
    client = AraOfflineClient()

ARA HTTP REST API client
~~~~~~~~~~~~~~~~~~~~~~~~

``AraHttpClient`` works with the same interface, methods and behavior as
``AraOfflineClient``.
The HTTP client does not require ``ara-server`` to be installed in order to be
used but expects a functional API endpoint at a specified location.

You can set your client to communicate with a remote ``ara-server`` API by
specifying an endpoint parameter::

    #!/usr/bin/env python3
    # Import the client
    from ara.clients.http import AraHttpClient

    # Instanciate the HTTP client with an endpoint where ara-server is listening
    client = AraHttpClient(endpoint="https://api.demo.recordsansible.org")

Example API usage
~~~~~~~~~~~~~~~~~

.. note::
   API documentation is a work in progress.

Once you've instanciated your client, you're ready to query the API.

Here's a code example to help you get started::

    # Get a list of failed playbooks
    # /api/v1/playbooks?status=failed
    playbooks = client.get("/api/v1/playbooks", status="failed")

    # If there are any failed playbooks, retrieve their failed results
    # and provide some insight.
    for playbook in playbooks["results"]:
        # Retrieve results for this playbook
        # /api/v1/results?playbook=<:id>&status=failed
        results = client.get("/api/v1/results", playbook=playbook["id"], status="failed")

        # Iterate over failed results to get meaningful data back
        for result in results["results"]:
            # Get the task that generated this result
            # /api/v1/tasks/<:id>
            task = client.get(f"/api/v1/tasks/{result['task']}")

            # Get the file from which this task ran from
            # /api/v1/files/<:id>
            file = client.get(f"/api/v1/files/{task['file']}")

            # Get the host on which this result happened
            # /api/v1/hosts/<:id>
            host = client.get(f"/api/v1/hosts/{result['host']}")

            # Print something useful
            print(f"Failure on {host['name']}: '{task['name']}' ({file['path']}:{task['lineno']})")
