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

import six
from ansible import __version__ as ansible_version
from ansible.plugins.callback import CallbackBase

from ara.clients.http import AraHttpClient
from ara.clients.offline import AraOfflineClient

# To retrieve Ansible CLI options
try:
    from __main__ import cli
except ImportError:
    cli = None


DOCUMENTATION = """
callback: ara
callback_type: notification
requirements:
  - ara-plugins
  - ara-server (when using the offline API client)
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
  api_timeout:
    description: Timeout, in seconds, before giving up on HTTP requests
    default: 30
    env:
      - name: ARA_API_TIMEOUT
    ini:
      - section: ara
        key: api_timeout
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

        self.result = None
        self.task = None
        self.play = None
        self.playbook = None
        self.stats = None
        self.loop_items = []

        if cli:
            self._options = cli.options
        else:
            self._options = None

    def set_options(self, task_keys=None, var_options=None, direct=None):
        super(CallbackModule, self).set_options(task_keys=task_keys, var_options=var_options, direct=direct)

        self.ignored_facts = self.get_option("ignored_facts")
        self.ignored_arguments = self.get_option("ignored_arguments")

        api_client = self.get_option("api_client")
        if api_client == "offline":
            self.client = AraOfflineClient()
        elif api_client == "http":
            server = self.get_option("api_server")
            timeout = self.get_option("api_timeout")
            self.client = AraHttpClient(endpoint=server, timeout=timeout)
        else:
            raise Exception("Unsupported API client: %s. Please use 'offline' or 'http'" % api_client)

    def v2_playbook_on_start(self, playbook):
        self.log.debug("v2_playbook_on_start")

        path = os.path.abspath(playbook._file_name)
        if self._options is not None:
            arguments = self._options.__dict__.copy()
        else:
            arguments = {}

        # Potentially sanitize some user-specified keys
        for argument in self.ignored_arguments:
            if argument in arguments:
                self.log.debug("Ignoring argument: %s" % argument)
                arguments[argument] = "Not saved by ARA as configured by 'ignored_arguments'"

        # Create the playbook
        self.playbook = self.client.post(
            "/api/v1/playbooks",
            ansible_version=ansible_version,
            arguments=arguments,
            status="running",
            file=dict(path=path, content=self._read_file(path)),
        )

        # Record all the files involved in the playbook
        self._load_files(playbook._loader._FILE_CACHE.keys())

        return self.playbook

    def v2_playbook_on_play_start(self, play):
        self.log.debug("v2_playbook_on_play_start")
        self._end_task()
        self._end_play()

        # Record all the files involved in the play
        self._load_files(play._loader._FILE_CACHE.keys())

        # Create the play
        self.play = self.client.post(
            "/api/v1/plays", name=play.name, status="running", uuid=play._uuid, playbook=self.playbook["id"]
        )

        # Record all the hosts involved in the play
        self._load_hosts(play._variable_manager._inventory._restriction)

        return self.play

    def v2_playbook_on_task_start(self, task, is_conditional, handler=False):
        self.log.debug("v2_playbook_on_task_start")
        self._end_task()

        pathspec = task.get_path()
        if pathspec:
            path, lineno = pathspec.split(":", 1)
            lineno = int(lineno)
        else:
            # Task doesn't have a path, default to "something"
            path = self.playbook["path"]
            lineno = 1

        # Ensure this task's file was added to the playbook -- files that are
        # dynamically included do not show up in the playbook or play context
        self._load_files([path])

        # Find the task file (is there a better way?)
        task_file = self.playbook["file"]["id"]
        for file in self.playbook["files"]:
            if file["path"] == path:
                task_file = file["id"]
                break

        self.task = self.client.post(
            "/api/v1/tasks",
            name=task.get_name(),
            action=task.action,
            play=self.play["id"],
            playbook=self.playbook["id"],
            file=task_file,
            tags=task._attributes["tags"],
            lineno=lineno,
            handler=handler,
        )

        return self.task

    def v2_runner_on_ok(self, result, **kwargs):
        self._load_result(result, "ok", **kwargs)

    def v2_runner_on_unreachable(self, result, **kwargs):
        self._load_result(result, "unreachable", **kwargs)

    def v2_runner_on_failed(self, result, **kwargs):
        self._load_result(result, "failed", **kwargs)

    def v2_runner_on_skipped(self, result, **kwargs):
        self._load_result(result, "skipped", **kwargs)

    def v2_playbook_on_stats(self, stats):
        self.log.debug("v2_playbook_on_stats")
        self._end_task()
        self._end_play()
        self._load_stats(stats)
        self._end_playbook(stats)

    def _end_task(self):
        if self.task is not None:
            self.client.patch(
                "/api/v1/tasks/%s" % self.task["id"], completed=True, ended=datetime.datetime.now().isoformat()
            )
            self.task = None
            self.loop_items = []

    def _end_play(self):
        if self.play is not None:
            self.client.patch(
                "/api/v1/plays/%s" % self.play["id"], status="completed", ended=datetime.datetime.now().isoformat()
            )
            self.play = None

    def _end_playbook(self, stats):
        status = "unknown"
        if len(stats.failures) >= 1 or len(stats.dark) >= 1:
            status = "failed"
        else:
            status = "completed"

        self.playbook = self.client.patch(
            "/api/v1/playbooks/%s" % self.playbook["id"], status=status, ended=datetime.datetime.now().isoformat()
        )

    def _load_files(self, files):
        self.log.debug("Loading %s file(s)..." % len(files))
        playbook_files = [file["path"] for file in self.playbook["files"]]
        for file in files:
            if file not in playbook_files:
                self.client.post(
                    "/api/v1/playbooks/%s/files" % self.playbook["id"], path=file, content=self._read_file(file)
                )

    def _get_or_create_host(self, host):
        self.log.debug("Getting or creating host: %s" % host)
        # Don't query the API if we already have this host
        for playbook_host in self.playbook["hosts"]:
            if host == playbook_host["name"]:
                return playbook_host

        # TODO: Implement logic for computing the host alias
        playbook_host = self.client.post("/api/v1/hosts", name=host, alias=host, playbook=self.playbook["id"])

        # Refresh cached playbook
        self.playbook = self.client.get("/api/v1/playbooks/%s" % self.playbook["id"])

        return playbook_host

    def _load_hosts(self, hosts):
        self.log.debug("Loading %s hosts(s)..." % len(hosts))
        for host in hosts:
            self._get_or_create_host(host)

    def _load_result(self, result, status, **kwargs):
        """
        This method is called when an individual task instance on a single
        host completes. It is responsible for logging a single result to the
        database.
        """
        host = self._get_or_create_host(result._host.get_name())

        # Use Ansible's CallbackBase._dump_results in order to strip internal
        # keys, respect no_log directive, etc.
        if self.loop_items:
            # NOTE (dmsimard): There is a known issue in which Ansible can send
            # callback hooks out of order and "exit" the task before all items
            # have returned, this can cause one of the items to be missing
            # from the task result in ARA.
            # https://github.com/ansible/ansible/issues/24207
            results = [self._dump_results(result._result)]
            for item in self.loop_items:
                results.append(self._dump_results(item._result))
            results = json.loads(json.dumps(results))
        else:
            results = json.loads(self._dump_results(result._result))

        self.result = self.client.post(
            "/api/v1/results",
            playbook=self.playbook["id"],
            task=self.task["id"],
            host=host["id"],
            content=results,
            status=status,
            started=self.task["started"],
            ended=datetime.datetime.now().isoformat(),
            changed=result._result.get("changed", False),
            failed=result._result.get("failed", False),
            skipped=result._result.get("skipped", False),
            unreachable=result._result.get("unreachable", False),
            ignore_errors=kwargs.get("ignore_errors", False),
        )

        if self.task["action"] == "setup" and "ansible_facts" in results:
            # Potentially sanitize some Ansible facts to prevent them from
            # being saved both in the host facts and in the task results.
            for fact in self.ignored_facts:
                if fact in results["ansible_facts"]:
                    self.log.debug("Ignoring fact: %s" % fact)
                    results["ansible_facts"][fact] = "Not saved by ARA as configured by 'ignored_facts'"

            self.client.patch("/api/v1/hosts/%s" % host["id"], facts=results["ansible_facts"])

    def _read_file(self, path):
        try:
            with open(path, "r") as fd:
                content = fd.read()
        except IOError as e:
            self.log.error("Unable to open {0} for reading: {1}".format(path, six.text_type(e)))
            content = """ARA was not able to read this file successfully.
                      Refer to the logs for more information"""
        return content

    def _load_stats(self, stats):
        hosts = sorted(stats.processed.keys())
        for hostname in hosts:
            host = self._get_or_create_host(hostname)
            host_stats = stats.summarize(hostname)
            self.client.post(
                "/api/v1/stats",
                playbook=self.playbook["id"],
                host=host["id"],
                changed=host_stats["changed"],
                unreachable=host_stats["unreachable"],
                failed=host_stats["failures"],
                ok=host_stats["ok"],
                skipped=host_stats["skipped"],
            )
