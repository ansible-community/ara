#!/usr/bin/env python3
# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Example using ara with ansible-runner
import json
import os

import ansible_runner

try:
    from ara.clients.utils import get_client
    from ara.setup import action_plugins, callback_plugins, lookup_plugins
except ImportError as e:
    print("ara must be installed first: https://github.com/ansible-community/ara#getting-started")
    raise e

PLAYBOOK = os.path.join(os.path.dirname(__file__), "runner-playbook.yml")


def main():
    # Configure Ansible to use the ara Ansible plugins
    os.environ["ANSIBLE_ACTION_PLUGINS"] = action_plugins
    os.environ["ANSIBLE_CALLBACK_PLUGINS"] = callback_plugins
    os.environ["ANSIBLE_LOOKUP_PLUGINS"] = lookup_plugins

    # Configure the ara callback (if necessary)
    os.environ["ARA_API_CLIENT"] = os.getenv("ARA_API_CLIENT", "offline")
    os.environ["ARA_API_SERVER"] = os.getenv("ARA_API_SERVER", "http://127.0.0.1:8000")
    os.environ["ARA_API_INSECURE"] = os.getenv("ARA_API_INSECURE", "false")
    os.environ["ARA_API_TIMEOUT"] = os.getenv("ARA_API_TIMEOUT", "15")
    os.environ["ARA_CALLBACK_THREADS"] = "4" if os.environ["ARA_API_CLIENT"] == "http" else "1"
    # Don't set these at all if they're not set (defaulting them to a blank or wrong value would fail authentication)
    if os.getenv("ARA_API_USERNAME"):
        os.environ["ARA_API_USERNAME"] = os.getenv("ARA_API_USERNAME")
    if os.getenv("ARA_API_PASSWORD"):
        os.environ["ARA_API_PASSWORD"] = os.getenv("ARA_API_PASSWORD")

    # Run a playbook with ansible
    # This example relies on the playbook creating a ./.ara_playbook file with the playbook id in it.
    # You could run any playbook so long as it provides a mechanism to retrieve the playbook id.
    ansible_runner.run(
        playbook=PLAYBOOK,
    )
    playbook_file = os.path.join(os.path.dirname(__file__), ".ara_playbook")
    with open(playbook_file) as f:
        playbook_id = f.read()

    # Retrieve an ara API client
    client = get_client(
        run_sql_migrations=False,
        client=os.environ["ARA_API_CLIENT"],
        endpoint=os.environ["ARA_API_SERVER"],
        timeout=os.environ["ARA_API_TIMEOUT"],
        username=os.environ["ARA_API_USERNAME"] if "ARA_API_USERNAME" in os.environ else None,
        password=os.environ["ARA_API_PASSWORD"] if "ARA_API_USERNAME" in os.environ else None,
        verify=False if os.environ["ARA_API_INSECURE"] else True,
    )

    # Get results for a particular task
    template = "{timestamp}: {host} {status} '{task}' ({task_file}:{lineno})"
    tasks = client.get("/api/v1/tasks", playbook=playbook_id, name="Dump the playbook id")
    task = tasks["results"][0]
    results = client.get("/api/v1/results", task=task["id"])
    for result in results["results"]:
        host = client.get("/api/v1/hosts/%s" % result["host"])

        print(
            template.format(
                timestamp=result["ended"],
                host=host["name"],
                status=result["status"],
                task=task["name"],
                task_file=task["path"],
                lineno=task["lineno"],
            )
        )

        # Result list doesn't have a detailed view of the result including the content
        detailed_result = client.get("/api/v1/results/%s" % result["id"])
        print(json.dumps(detailed_result["content"], indent=2))


if __name__ == "__main__":
    main()
