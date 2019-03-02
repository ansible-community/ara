Using ARA API clients
=====================

When installing ARA, you are provided with an API server and two API clients
out of the box:

- ``AraOfflineClient`` can query the API without needing an API server to be running
- ``AraHttpClient`` is meant to query a specified API server over http

ARA Offline REST API client
~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your use case doesn't require a remote or persistent API server, the offline
client lets you query the API without needing to start an API server.

In order to use this client, you would instanciate it like this::

    #!/usr/bin/env python3
    # Import the client
    from ara.clients.offline import AraOfflineClient

    # Instanciate the offline client
    client = AraOfflineClient()

ARA HTTP REST API client
~~~~~~~~~~~~~~~~~~~~~~~~

``AraHttpClient`` works with the same interface, methods and behavior as
``AraOfflineClient``.

You can set your client to communicate with a remote ``ara-server`` API by
specifying an endpoint parameter::

    #!/usr/bin/env python3
    # Import the client
    from ara.clients.http import AraHttpClient

    # Instanciate the HTTP client with an endpoint where an API server is listening
    client = AraHttpClient(endpoint="https://api.demo.recordsansible.org")

Example API usage
~~~~~~~~~~~~~~~~~

.. note::
   API documentation is a work in progress.

Once you've instanciated your client, you're ready to query the API.

Here's a code example to help you get started::

    #!/usr/bin/env python3
    # Import the client
    from ara.clients.http import AraHttpClient

    # Instanciate the HTTP client with an endpoint where an API server is listening
    client = AraHttpClient(endpoint="https://api.demo.recordsansible.org")

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
