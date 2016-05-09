# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import (absolute_import, division, print_function)

import os
import datetime
import uuid

from ara import app, db, models
from ansible.plugins.callback import CallbackBase
try:
    import simplejson as json
except ImportError:
    import json

__metaclass__ = type


class CallbackModule(CallbackBase):
    """
    Saves data from an Ansible run into an sqlite database
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'ara'

    DATABASE = app.config['DATABASE']

    def __init__(self):
        super(CallbackModule, self).__init__()

        # TODO (dmsimard): Figure out the best place and way to initialize the
        #                  database if it hasn't been created yet.
        if not os.path.exists(os.path.dirname(self.DATABASE)):
            os.makedirs(os.path.dirname(self.DATABASE))
        db.create_all()

        self.task = None
        self.play = None
        self.playbook = None
        self.playbook_uuid = None
        self.playbook_start = None
        self.playbook_end = None
        self.stats = None
        self.task_start = None

    def log_task(self, result):
        duration = (result.task_end - result.task_start).total_seconds()
        data = models.Tasks(**{
            'playbook_uuid': self.playbook_uuid,
            'host':          result._host.name,
            'play':          self.play.name,
            'task':          self.task.name,
            'module':        self.task.action,
            'start':         str(result.task_start),
            'end':           str(result.task_end),
            'duration':      duration,
            'result':        json.dumps(result._result),
            'changed':       result._result['changed'],
            'skipped':       result._result['skipped'],
            'failed':        result._result['failed'],
            'ignore_errors': self.task.ignore_errors or False
        })
        db.session.add(data)

    def log_stats(self, stats):
        hosts = sorted(stats.processed.keys())
        for host in hosts:
            host_stats = stats.summarize(host)
            data = models.Stats(**{
                'playbook_uuid': self.playbook_uuid,
                'host':          host,
                'changed':       host_stats['changed'],
                'failures':      host_stats['failures'],
                'ok':            host_stats['ok'],
                'skipped':       host_stats['skipped']
            })
            db.session.add(data)

    def log_playbook(self):
        duration = (self.playbook_end - self.playbook_start).total_seconds()
        data = models.Playbooks(**{
            'id': self.playbook_uuid,
            'playbook': os.path.basename(self.playbook._file_name),
            'start': str(self.playbook_start),
            'end': str(self.playbook_end),
            'duration': duration
        })
        db.session.add(data)

    def v2_runner_on_ok(self, result, **kwargs):
        self.task = result._task
        result.task_start = self.task_start
        result.task_end = datetime.datetime.now()

        status_keys = ['changed', 'failed', 'skipped']
        for status in status_keys:
            if status not in result._result:
                result._result[status] = False

        self.log_task(result)

    v2_runner_on_unreachable = v2_runner_on_ok
    v2_runner_on_failed = v2_runner_on_ok
    v2_runner_on_skipped = v2_runner_on_ok

    def v2_playbook_on_task_start(self, task, is_conditional):
        self.task_start = datetime.datetime.now()

    def v2_playbook_on_start(self, playbook):
        self.playbook = playbook
        self.playbook_uuid = str(uuid.uuid4())
        self.playbook_start = datetime.datetime.now()

    def v2_playbook_on_play_start(self, play):
        self.play = play

    def v2_playbook_on_stats(self, stats):
        self.playbook_end = datetime.datetime.now()
        self.log_stats(stats)
        self.log_playbook()
        db.session.commit()
