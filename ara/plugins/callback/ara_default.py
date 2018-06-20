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

from __future__ import (absolute_import, division, print_function)

import datetime
import logging
import os
import six

from ara.clients.offline import Client as offline_client
# from ara.clients.online import Client as online_client
from ansible import __version__ as ansible_version
from ansible.plugins.callback import CallbackBase
# To retrieve Ansible CLI options
try:
    from __main__ import cli
except ImportError:
    cli = None


class CallbackModule(CallbackBase):
    """
    Saves data from an Ansible run into a database
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'awesome'
    CALLBACK_NAME = 'ara_default'

    def __init__(self):
        super(CallbackModule, self).__init__()
        self.log = logging.getLogger('ara.plugins.callback.default')

        # TODO: logic for picking between offline and online client
        self.client = offline_client()

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

    def v2_playbook_on_start(self, playbook):
        self.log.debug('v2_playbook_on_start')

        path = os.path.abspath(playbook._file_name)
        if self._options is not None:
            parameters = self._options.__dict__.copy()
        else:
            parameters = {}

        # Create the playbook
        self.playbook = self.client.post(
            '/api/v1/playbooks/',
            ansible_version=ansible_version,
            parameters=parameters,
            file=dict(
                path=path,
                content=self._read_file(path)
            )
        )

        # Record all the files involved in the playbook
        self._load_files(playbook._loader._FILE_CACHE.keys())

        return self.playbook

    def v2_playbook_on_play_start(self, play):
        self.log.debug('v2_playbook_on_play_start')
        self._end_task()
        self._end_play()

        # Record all the files involved in the play
        self._load_files(play._loader._FILE_CACHE.keys())

        # Create the play
        self.play = self.client.post(
            '/api/v1/plays/',
            name=play.name,
            playbook=self.playbook['id']
        )

        return self.play

    def v2_playbook_on_task_start(self, task, is_conditional, handler=False):
        self.log.debug('v2_playbook_on_task_start')
        self._end_task()

        pathspec = task.get_path()
        if pathspec:
            path, lineno = pathspec.split(':', 1)
            lineno = int(lineno)
        else:
            # Task doesn't have a path, default to "something"
            path = self.playbook['path']
            lineno = 1

        # Ensure this task's file was added to the playbook -- files that are
        # dynamically included do not show up in the playbook or play context
        self._load_files([path])

        # Find the task file (is there a better way?)
        task_file = self.playbook['file']['id']
        for file in self.playbook['files']:
            if file['path'] == path:
                task_file = file['id']
                break

        self.task = self.client.post(
            '/api/v1/tasks/',
            name=task.get_name(),
            action=task.action,
            play=self.play['id'],
            playbook=self.playbook['id'],
            file=task_file,
            tags=task._attributes['tags'],
            lineno=lineno,
            handler=handler
        )

        return self.task

    def v2_playbook_on_stats(self, stats):
        self.log.debug('v2_playbook_on_stats')

        self._end_task()
        self._end_play()
        self._end_playbook()

    def _end_task(self):
        if self.task is not None:
            self.client.patch(
                '/api/v1/tasks/%s/' % self.task['id'],
                completed=True,
                ended=datetime.datetime.now().isoformat()
            )
            self.task = None
            self.loop_items = []

    def _end_play(self):
        if self.play is not None:
            self.client.patch(
                '/api/v1/plays/%s/' % self.play['id'],
                completed=True,
                ended=datetime.datetime.now().isoformat()
            )
            self.play = None

    def _end_playbook(self):
        self.playbook = self.client.patch(
            '/api/v1/playbooks/%s/' % self.playbook['id'],
            completed=True,
            ended=datetime.datetime.now().isoformat()
        )

    def _load_files(self, files):
        self.log.debug('Loading %s file(s)...' % len(files))
        playbook_files = [file['path'] for file in self.playbook['files']]
        for file in files:
            if file not in playbook_files:
                self.client.post(
                    '/api/v1/playbooks/%s/files/' % self.playbook['id'],
                    path=file,
                    content=self._read_file(file)
                )

    def _read_file(self, path):
        try:
            with open(path, 'r') as fd:
                content = fd.read()
        except IOError as e:
            self.log.error("Unable to open {0} for reading: {1}".format(
                path, six.text_type(e)
            ))
            content = """ARA was not able to read this file successfully.
                      Refer to the logs for more information"""
        return content
