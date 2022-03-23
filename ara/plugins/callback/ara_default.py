#  Copyright (c) 2018 Red Hat, Inc.
#
#  This file is part of ARA: Ansible Run Analysis.
#
#  ARA is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  ARA is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with ARA.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, division, print_function

import datetime
import json
import logging
import os
import socket
from concurrent.futures import ThreadPoolExecutor

from ansible import __version__ as ansible_version
from ansible.parsing.ajson import AnsibleJSONEncoder
from ansible.plugins.callback import CallbackBase
from ansible.vars.clean import module_response_deepcopy, strip_internal_keys

from ara.clients import utils as client_utils

# Ansible CLI options are now in ansible.context in >= 2.8
# https://github.com/ansible/ansible/commit/afdbb0d9d5bebb91f632f0d4a1364de5393ba17a
try:
    from ansible import context

    cli_options = {key: value for key, value in context.CLIARGS.items()}
except ImportError:
    # < 2.8 doesn't have ansible.context
    try:
        from __main__ import cli

        cli_options = cli.options.__dict__
    except ImportError:
        # using API without CLI
        cli_options = {}


DOCUMENTATION = """
callback: ara
callback_type: notification
requirements:
  - ara
short_description: Sends playbook execution data to the ARA API internally or over HTTP
description:
  - Sends playbook execution data to the ARA API internally or over HTTP
options:
  api_client:
    description: The client to use for communicating with the API
    default: offline
    env:
      - name: ARA_API_CLIENT
    ini:
      - section: ara
        key: api_client
    choices: ['offline', 'http']
  api_server:
    description: When using the HTTP client, the base URL to the ARA API server
    default: http://127.0.0.1:8000
    env:
      - name: ARA_API_SERVER
    ini:
      - section: ara
        key: api_server
  api_username:
    description: If authentication is required, the username to authenticate with
    default: null
    env:
      - name: ARA_API_USERNAME
    ini:
      - section: ara
        key: api_username
  api_password:
    description: If authentication is required, the password to authenticate with
    default: null
    env:
      - name: ARA_API_PASSWORD
    ini:
      - section: ara
        key: api_password
  api_insecure:
    description: Can be enabled to ignore SSL certification of the API server
    type: bool
    default: false
    env:
      - name: ARA_API_INSECURE
    ini:
      - section: ara
        key: api_insecure
  api_timeout:
    description: Timeout, in seconds, before giving up on HTTP requests
    type: integer
    default: 30
    env:
      - name: ARA_API_TIMEOUT
    ini:
      - section: ara
        key: api_timeout
  argument_labels:
    description: |
        A list of CLI arguments that, if set, will be automatically applied to playbooks as labels.
        Note that CLI arguments are not always named the same as how they are represented by Ansible.
        For example, --limit is "subset", --user is "remote_user" but --check is "check".
    type: list
    default:
      - remote_user
      - check
      - tags
      - skip_tags
      - subset
    env:
      - name: ARA_ARGUMENT_LABELS
    ini:
      - section: ara
        key: argument_labels
  default_labels:
    description: A list of default labels that will be applied to playbooks
    type: list
    default: []
    env:
      - name: ARA_DEFAULT_LABELS
    ini:
      - section: ara
        key: default_labels
  ignored_facts:
    description: List of host facts that will not be saved by ARA
    type: list
    default: ["ansible_env"]
    env:
      - name: ARA_IGNORED_FACTS
    ini:
      - section: ara
        key: ignored_facts
  ignored_arguments:
    description: List of Ansible arguments that will not be saved by ARA
    type: list
    default: ["extra_vars"]
    env:
      - name: ARA_IGNORED_ARGUMENTS
    ini:
      - section: ara
        key: ignored_arguments
  ignored_files:
    description: List of patterns that will not be saved by ARA
    type: list
    default: []
    env:
      - name: ARA_IGNORED_FILES
    ini:
      - section: ara
        key: ignored_files
  localhost_as_hostname:
    description:
        - Associates results to the hostname (or fqdn) instead of localhost when the inventory name is localhost
        - Defaults to false for backwards compatibility, set to true to enable
        - This can be useful when targetting localhost, using ansible-pull or ansible-playbook -i 'localhost,'
        - This helps differentiating results between hosts, otherwise everything would be recorded under localhost.
    type: boolean
    default: false
    env:
      - name: ARA_LOCALHOST_AS_HOSTNAME
    ini:
      - section: ara
        key: localhost_as_hostname
  localhost_as_hostname_format:
    description:
      - The format to use when recording the hostname for localhost
      - This is used when recording the controller hostname or when ARA_LOCALHOST_TO_HOSTNAME is true
      - There are different formats to choose from based on the full (or short) configured hostname and fqdn
      - Defaults to 'fqdn' (i.e, server.example.org) but can be set to 'fqdn_short' (server)
      - Other options include 'hostname' and 'hostname_short' which may be suitable depending on server configuration
    default: fqdn
    env:
      - name: ARA_LOCALHOST_AS_HOSTNAME_FORMAT
    ini:
      - section: ara
        key: localhost_as_hostname_format
    choices: ['fqdn', 'fqdn_short', 'hostname', 'hostname_short']
  callback_threads:
    description:
      - The number of threads to use in API client thread pools
      - When set to 0, no threading will be used (default) which is appropriate for usage with sqlite
      - Using threads is recommended when the server is using MySQL or PostgreSQL
    type: integer
    default: 0
    env:
      - name: ARA_CALLBACK_THREADS
    ini:
      - section: ara
        key: callback_threads
"""


class CallbackModule(CallbackBase):
    """
    Saves data from an Ansible run into a database
    """

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "awesome"
    CALLBACK_NAME = "ara_default"

    def __init__(self):
        super(CallbackModule, self).__init__()
        self.log = logging.getLogger("ara.plugins.callback.default")
        self.localhost_hostname = None
        # These are configured in self.set_options
        self.client = None
        self.callback_threads = None

        self.ignored_facts = []
        self.ignored_arguments = []
        self.ignored_files = []
        self.localhost_as_hostname = None
        self.localhost_as_hostname_format = None

        self.result = None
        self.result_started = {}
        self.result_ended = {}
        self.task = None
        self.play = None
        self.playbook = None
        self.stats = None
        self.file_cache = {}
        self.host_cache = {}
        self.task_cache = {}
        self.delegation_cache = {}

    def set_options(self, task_keys=None, var_options=None, direct=None):
        super(CallbackModule, self).set_options(task_keys=task_keys, var_options=var_options, direct=direct)

        self.argument_labels = self.get_option("argument_labels")
        self.default_labels = self.get_option("default_labels")
        self.ignored_facts = self.get_option("ignored_facts")
        self.ignored_arguments = self.get_option("ignored_arguments")
        self.ignored_files = self.get_option("ignored_files")
        self.localhost_as_hostname = self.get_option("localhost_as_hostname")
        self.localhost_as_hostname_format = self.get_option("localhost_as_hostname_format")

        client = self.get_option("api_client")
        endpoint = self.get_option("api_server")
        timeout = self.get_option("api_timeout")
        username = self.get_option("api_username")
        password = self.get_option("api_password")
        insecure = self.get_option("api_insecure")
        self.client = client_utils.get_client(
            client=client,
            endpoint=endpoint,
            timeout=timeout,
            username=username,
            password=password,
            verify=False if insecure else True,
        )

        # TODO: Consider un-hardcoding this and plumbing pool_maxsize to requests.adapters.HTTPAdapter.
        #       In the meantime default to 4 so we don't go above requests.adapters.DEFAULT_POOLSIZE.
        #       Otherwise we can hit "urllib3.connectionpool: Connection pool is full"
        self.callback_threads = self.get_option("callback_threads")
        if self.callback_threads > 4:
            self.callback_threads = 4

    def _submit_thread(self, threadpool, func, *args, **kwargs):
        # Manages whether or not the function should be threaded to keep things DRY
        if self.callback_threads:
            # Pick from one of two thread pools (global or task)
            threads = getattr(self, threadpool + "_threads")
            threads.submit(func, *args, **kwargs)
        else:
            func(*args, **kwargs)

    def v2_playbook_on_start(self, playbook):
        self.log.debug("v2_playbook_on_start")

        # Lookup the hostname for localhost if necessary
        self.localhost_hostname = self._get_localhost_hostname()

        if self.callback_threads:
            self.global_threads = ThreadPoolExecutor(max_workers=self.callback_threads)
            self.log.debug("Global thread pool initialized with %s thread(s)" % self.callback_threads)

        content = None

        if playbook._file_name == "__adhoc_playbook__":
            content = cli_options["module_name"]
            if cli_options["module_args"]:
                content = "{0}: {1}".format(content, cli_options["module_args"])
            path = "Ad-Hoc: {0}".format(content)
        else:
            path = os.path.abspath(playbook._file_name)

        # Potentially sanitize some user-specified keys
        for argument in self.ignored_arguments:
            if argument in cli_options:
                self.log.debug("Ignoring argument: %s" % argument)
                cli_options[argument] = "Not saved by ARA as configured by 'ignored_arguments'"

        # Retrieve and format CLI options for argument labels
        argument_labels = []
        for label in self.argument_labels:
            if label in cli_options:
                # Some arguments are lists or tuples
                if isinstance(cli_options[label], tuple) or isinstance(cli_options[label], list):
                    # Only label these if they're not empty
                    if cli_options[label]:
                        argument_labels.append("%s:%s" % (label, ",".join(cli_options[label])))
                # Some arguments are booleans
                elif isinstance(cli_options[label], bool):
                    argument_labels.append("%s:%s" % (label, cli_options[label]))
                # The rest can be printed as-is if there is something set
                elif cli_options[label]:
                    argument_labels.append("%s:%s" % (label, cli_options[label]))
        self.argument_labels = argument_labels

        # Create the playbook
        self.playbook = self.client.post(
            "/api/v1/playbooks",
            ansible_version=ansible_version,
            arguments=cli_options,
            status="running",
            path=path,
            controller=self.localhost_hostname,
            started=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        )

        # Record the playbook file
        self._submit_thread("global", self._get_or_create_file, path, content)

        return self.playbook

    def v2_playbook_on_play_start(self, play):
        self.log.debug("v2_playbook_on_play_start")
        self._end_task()
        self._end_play()

        # Load variables to verify if there is anything relevant for ara
        play_vars = play._variable_manager.get_vars(play=play)["vars"]
        if "ara_playbook_name" in play_vars:
            self._submit_thread("global", self._set_playbook_name, play_vars["ara_playbook_name"])

        labels = self.default_labels + self.argument_labels
        if "ara_playbook_labels" in play_vars:
            # ara_playbook_labels can be supplied as a list inside a playbook
            # but it might also be specified as a comma separated string when
            # using extra-vars
            if isinstance(play_vars["ara_playbook_labels"], list):
                labels.extend(play_vars["ara_playbook_labels"])
            elif isinstance(play_vars["ara_playbook_labels"], str):
                labels.extend(play_vars["ara_playbook_labels"].split(","))
            else:
                raise TypeError("ara_playbook_labels must be a list or a comma-separated string")
        if labels:
            self._submit_thread("global", self._set_playbook_labels, labels)

        # Record all the files involved in the play
        for path in play._loader._FILE_CACHE.keys():
            self._submit_thread("global", self._get_or_create_file, path)

        # Note: ansible-runner suffixes play UUIDs when running in serial so 34cff6f4-9f8e-6137-3461-000000000005 can
        # end up being 34cff6f4-9f8e-6137-3461-000000000005_2. Remove anything beyond standard 36 character UUIDs.
        # https://github.com/ansible-community/ara/issues/211
        # Create the play
        self.play = self.client.post(
            "/api/v1/plays",
            name=play.name,
            status="running",
            uuid=play._uuid[:36],
            playbook=self.playbook["id"],
            started=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        )

        return self.play

    def v2_playbook_on_handler_task_start(self, task):
        self.log.debug("v2_playbook_on_handler_task_start")
        # TODO: Why doesn't `v2_playbook_on_handler_task_start` have is_conditional ?
        self.v2_playbook_on_task_start(task, False, handler=True)

    def v2_playbook_on_task_start(self, task, is_conditional, handler=False):
        self.log.debug("v2_playbook_on_task_start")
        self._end_task()

        if self.callback_threads:
            self.task_threads = ThreadPoolExecutor(max_workers=self.callback_threads)
            self.log.debug("Task thread pool initialized with %s thread(s)" % self.callback_threads)

        pathspec = task.get_path()
        if pathspec:
            path, lineno = pathspec.split(":", 1)
            lineno = int(lineno)
        else:
            # Task doesn't have a path, default to "something"
            path = self.playbook["path"]
            lineno = 1

        # Get task file
        task_file = self._get_or_create_file(path)

        # Get task
        self.task = self._get_or_create_task(task, task_file["id"], lineno, handler)

        return self.task

    def v2_runner_on_start(self, host, task):
        self.log.debug("v2_runner_on_start")
        # v2_runner_on_start was added in 2.8 so this doesn't get run for Ansible 2.7 and below.
        self.result_started[host.get_name()] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    def v2_runner_on_ok(self, result, **kwargs):
        self.log.debug("v2_runner_on_ok")
        self._submit_thread("task", self._load_result, result, "ok", **kwargs)

    def v2_runner_on_unreachable(self, result, **kwargs):
        self.log.debug("v2_runner_on_unreachable")
        self._submit_thread("task", self._load_result, result, "unreachable", **kwargs)

    def v2_runner_on_failed(self, result, **kwargs):
        self.log.debug("v2_runner_on_failed")
        self._submit_thread("task", self._load_result, result, "failed", **kwargs)

    def v2_runner_on_skipped(self, result, **kwargs):
        self.log.debug("v2_runner_on_skipped")
        self._submit_thread("task", self._load_result, result, "skipped", **kwargs)

    def v2_runner_item_on_ok(self, result):
        self.log.debug("v2_runner_item_on_ok")
        self._update_delegation_cache(result)

    def v2_runner_item_on_failed(self, result):
        self.log.debug("v2_runner_item_on_failed")
        self._update_delegation_cache(result)

    def v2_runner_item_on_skipped(self, result):
        self.log.debug("v2_runner_item_on_skipped")
        pass
        # result._task.delegate_to can end up being a variable from this hook, don't save it.
        # https://github.com/ansible/ansible/issues/75339
        # self._update_delegation_cache(result)

    def v2_playbook_on_include(self, included_file):
        self.log.debug("v2_playbook_on_include")
        # ara has not used this hook before, maybe we can do something with it in the future.
        pass

    def v2_playbook_on_stats(self, stats):
        self.log.debug("v2_playbook_on_stats")
        self._end_task()
        self._end_play()
        self._load_stats(stats)
        self._end_playbook(stats)

    def _end_task(self):
        if self.task is not None:
            self._submit_thread(
                "task",
                self.client.patch,
                "/api/v1/tasks/%s" % self.task["id"],
                status="completed",
                ended=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            )
            if self.callback_threads:
                # Flush threads before moving on to next task to make sure all results are saved
                self.log.debug("waiting for task threads...")
                self.task_threads.shutdown(wait=True)
                self.task_threads = None
            self.task = None

    def _end_play(self):
        if self.play is not None:
            self._submit_thread(
                "global",
                self.client.patch,
                "/api/v1/plays/%s" % self.play["id"],
                status="completed",
                ended=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            )
            self.play = None

    def _end_playbook(self, stats):
        status = "unknown"
        if len(stats.failures) >= 1 or len(stats.dark) >= 1:
            status = "failed"
        else:
            status = "completed"

        self._submit_thread(
            "global",
            self.client.patch,
            "/api/v1/playbooks/%s" % self.playbook["id"],
            status=status,
            ended=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        )

        if self.callback_threads:
            self.log.debug("waiting for global threads...")
            self.global_threads.shutdown(wait=True)

    def _set_playbook_name(self, name):
        if self.playbook["name"] != name:
            self.playbook = self.client.patch("/api/v1/playbooks/%s" % self.playbook["id"], name=name)

    def _set_playbook_labels(self, labels):
        # Only update labels if our cache doesn't match
        current_labels = [label["name"] for label in self.playbook["labels"]]
        if sorted(current_labels) != sorted(labels):
            self.log.debug("Updating playbook labels to match: %s" % ",".join(labels))
            self.playbook = self.client.patch("/api/v1/playbooks/%s" % self.playbook["id"], labels=labels)

    def _get_or_create_file(self, path, content=None):
        if path not in self.file_cache:
            self.log.debug("File not in cache, getting or creating: %s" % path)
            for ignored_file_pattern in self.ignored_files:
                if ignored_file_pattern in path:
                    self.log.debug("Ignoring file {1}, matched pattern: {0}".format(ignored_file_pattern, path))
                    content = "Not saved by ARA as configured by 'ignored_files'"
            if content is None:
                try:
                    with open(path, "r") as fd:
                        content = fd.read()
                except IOError as e:
                    self.log.error("Unable to open {0} for reading: {1}".format(path, str(e)))
                    content = """ARA was not able to read this file successfully.
                            Refer to the logs for more information"""

            self.file_cache[path] = self.client.post(
                "/api/v1/files", playbook=self.playbook["id"], path=path, content=content
            )

        return self.file_cache[path]

    def _get_or_create_host(self, host):
        """ Note: The get_or_create is handled through the serializer of the API server. """
        # We might want to record results against the fqdn instead of localhost
        # so that we can differentiate between different actual hosts
        if self.localhost_as_hostname and host in ["localhost", "127.0.0.1"]:
            host = self.localhost_hostname

        if host not in self.host_cache:
            self.log.debug("Host not in cache, getting or creating: %s" % host)
            self.host_cache[host] = self.client.post("/api/v1/hosts", name=host, playbook=self.playbook["id"])
        return self.host_cache[host]

    def _get_or_create_task(self, task, file_id=None, lineno=None, handler=None):
        # Note: The get_or_create is handled through the serializer of the API server.
        task_uuid = str(task._uuid)[:36]
        if task_uuid not in self.task_cache:
            if None in (file_id, lineno, handler):
                raise ValueError("file_id, lineno, and handler are required to create a task")

            self.log.debug("Task not in cache, getting or creating: %s" % task)
            self.task_cache[task_uuid] = self.client.post(
                "/api/v1/tasks",
                name=task.get_name(),
                status="running",
                action=task.action,
                play=self.play["id"],
                playbook=self.playbook["id"],
                file=file_id,
                tags=task.tags,
                lineno=lineno,
                handler=handler,
                started=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            )

        return self.task_cache[task_uuid]

    def _update_delegation_cache(self, result):
        # If the task is a loop and delegate_to is a variable, result._task.delegate_to can return the variable
        # instead of it's value when using the v2_runner_on_* hooks.
        # We're caching the actual host names here from v2_runner_item_on_* hooks.
        # https://github.com/ansible/ansible/issues/75339
        if result._task.delegate_to:
            task_uuid = str(result._task._uuid[:36])
            if task_uuid not in self.delegation_cache:
                self.delegation_cache[task_uuid] = []
            self.delegation_cache[task_uuid].append(result._task.delegate_to)

    def _load_result(self, result, status, **kwargs):
        """
        This method is called when an individual task instance on a single
        host completes. It is responsible for logging a single result to the
        database.
        """
        hostname = result._host.get_name()
        self.result_ended[hostname] = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Retrieve the host so we can associate the result to the host id
        host = self._get_or_create_host(hostname)

        # If the task was delegated to another host, retrieve that too.
        # Since a single task can be delegated to multiple hosts (ex: looping on a host group and using delegate_to)
        # this must be a list of hosts.
        delegated_to = []
        # The value of result._task.delegate_to doesn't get templated if the task was skipped
        # https://github.com/ansible/ansible/issues/75339#issuecomment-888724838
        if result._task.delegate_to and status != "skipped":
            task_uuid = str(result._task._uuid[:36])
            if task_uuid in self.delegation_cache:
                for delegated in self.delegation_cache[task_uuid]:
                    delegated_to.append(self._get_or_create_host(delegated))
            else:
                delegated_to.append(self._get_or_create_host(result._task.delegate_to))

        # Retrieve the task so we can associate the result to the task id
        task = self._get_or_create_task(result._task)

        results = strip_internal_keys(module_response_deepcopy(result._result))

        # Round-trip through JSON to sort keys and convert Ansible types
        # to standard types
        try:
            jsonified = json.dumps(results, cls=AnsibleJSONEncoder, ensure_ascii=False, sort_keys=True)
        except TypeError:
            # Python 3 can't sort non-homogenous keys.
            # https://bugs.python.org/issue25457
            jsonified = json.dumps(results, cls=AnsibleJSONEncoder, ensure_ascii=False, sort_keys=False)
        results = json.loads(jsonified)

        # Sanitize facts
        if "ansible_facts" in results:
            for fact in self.ignored_facts:
                if fact in results["ansible_facts"]:
                    self.log.debug("Ignoring fact: %s" % fact)
                    results["ansible_facts"][fact] = "Not saved by ARA as configured by 'ignored_facts'"

        self.result = self.client.post(
            "/api/v1/results",
            playbook=self.playbook["id"],
            task=task["id"],
            host=host["id"],
            delegated_to=[h["id"] for h in delegated_to],
            play=task["play"],
            content=results,
            status=status,
            started=self.result_started[hostname] if hostname in self.result_started else task["started"],
            ended=self.result_ended[hostname],
            changed=result._result.get("changed", False),
            # Note: ignore_errors might be None instead of a boolean
            ignore_errors=kwargs.get("ignore_errors", False) or False,
        )

        if task["action"] in ["setup", "gather_facts"] and "ansible_facts" in results:
            self.client.patch("/api/v1/hosts/%s" % host["id"], facts=results["ansible_facts"])

    def _load_stats(self, stats):
        hosts = sorted(stats.processed.keys())
        for hostname in hosts:
            host = self._get_or_create_host(hostname)
            host_stats = stats.summarize(hostname)

            self._submit_thread(
                "global",
                self.client.patch,
                "/api/v1/hosts/%s" % host["id"],
                changed=host_stats["changed"],
                unreachable=host_stats["unreachable"],
                failed=host_stats["failures"],
                ok=host_stats["ok"],
                skipped=host_stats["skipped"],
            )

    def _get_localhost_hostname(self):
        """ Returns a hostname for localhost in the specified format """
        hostname = None

        if self.localhost_as_hostname_format.startswith("fqdn"):
            hostname = socket.getfqdn()

        if self.localhost_as_hostname_format.startswith("hostname"):
            hostname = socket.gethostname()

        # Shouldn't happen but we never know ¯\_(ツ)_/¯
        if hostname is None:
            raise Exception("Unable to resolve a hostname for localhost")

        if self.localhost_as_hostname_format.endswith("_short"):
            return hostname.split(".")[0]

        return hostname
