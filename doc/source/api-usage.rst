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

In order to use this client, you would instanciate it like this::

    #!/usr/bin/env python3
    # Import the client
    from ara.clients.offline import AraOfflineClient

    # Instanciate the offline client
    client = AraOfflineClient()

ARA HTTP API client
~~~~~~~~~~~~~~~~~~~

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

For more details on the API endpoints, see :ref:`api-documentation:API Documentation`.

Otherwise, once you've instanciated your client, you're ready to query the API.

Here's a code example to help you get started:

.. code-block:: python

    #!/usr/bin/env python3
    # Import the client
    from ara.clients.http import AraHttpClient

    # Instanciate the HTTP client with an endpoint where an API server is listening
    client = AraHttpClient(endpoint="https://api.demo.recordsansible.org")

    # Get a list of failed playbooks
    # /api/v1/playbooks?status=failed
    playbooks = client.get("/api/v1/playbooks", status="failed")

    # If there are any results from our query, get more information about the
    # failure and print something helpful
    template = "{timestamp}: {host} failed '{task}' ({task_file}:{lineno})"
    for playbook in playbooks["results"]:
        # Get a detailed version of the playbook that provides additional context
        detailed_playbook = client.get("/api/v1/playbooks/%s" % playbook["id"])

        # Iterate through the playbook to get the context
        # Playbook -> Play -> Task -> Result <- Host
        for play in detailed_playbook["plays"]:
            for task in play["tasks"]:
                for result in task["results"]:
                    if result["status"] in ["failed", "unreachable"]:
                        print(template.format(
                            timestamp=result["ended"],
                            host=result["host"]["name"],
                            task=task["name"],
                            task_file=task["file"]["path"],
                            lineno=task["lineno"]
                        ))

Running this script would then provide an output that looks like the following::

    2019-03-20T16:18:41.710765: localhost failed 'smoke-tests : Return false' (tests/integration/roles/smoke-tests/tasks/test-ops.yaml:25)
    2019-03-20T16:19:17.332663: localhost failed 'fail' (tests/integration/failed.yaml:22)
