#   Copyright 2016 Red Hat, Inc. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

from __future__ import (absolute_import, division, print_function)

import logging
import os
import itertools
from datetime import datetime
from decorator import decorator

from ara import app, db, models
from ansible.plugins.callback import CallbackBase
try:
    import simplejson as json
except ImportError:
    import json

__metaclass__ = type

LOG = logging.getLogger('ara.callback')


def commit(*attrs):
    '''This will commit the given attributes of `self` after the
    wrapped function exists.  For example, if you write:

        @commit('task', 'play')
        def myfunc(self):
          ...code goes here...

    Then after `myfunc` exits, this decorator would run the equivalent of:

        db.session.add(self.task)
        db.sessiona.add(self.play)
        db.commit()
    '''

    def _commit(f, self, *args, **kwargs):
        rval = f(self, *args, **kwargs)
        for attr in attrs:
            actual = getattr(self, attr)
            if actual is None:
                LOG.error('delcining to track null attribute %s', attr)
                continue
            db.session.add(actual)

        db.session.commit()
        return rval

    return decorator(_commit)


class IncludeResult(object):
    '''This is used by the v2_playbook_on_include callback to synthesize
    a task result for calling log_task.'''
    def __init__(self, host, path):
        self._host = host
        self._result = {'included_file': path}


class CallbackModule(CallbackBase):
    '''
    Saves data from an Ansible run into an sqlite database
    '''
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'ara'

    def __init__(self):
        super(CallbackModule, self).__init__()

        self.taskresult = None
        self.task = None
        self.play = None
        self.playbook = None
        self.stats = None

        self.play_counter = itertools.count()
        self.task_counter = itertools.count()

    def get_or_create_host(self, hostname):
        try:
            host = models.Host.query.filter_by(name=hostname).one()
        except models.NoResultFound:
            host = models.Host(name=hostname)
            db.session.add(host)

        return host

    @commit('taskresult')
    def log_task(self, result, status, **kwargs):
        '''`log_task` is called when an individual task instance on a single
        host completes. It is responsible for logging a single
        `TaskResult` record to the database.'''
        LOG.debug('logging task result for task %s (%s), host %s',
                  self.task.name, self.task.id, result._host.name)

        result.task_start = self.task.time_start
        result.task_end = datetime.now()
        host = self.get_or_create_host(result._host.name)
        host.playbooks.append(self.playbook)

        self.taskresult = models.TaskResult(
            task=self.task,
            host=host,
            time_start=result.task_start,
            time_end=result.task_end,
            result=json.dumps(result._result),
            status=status,
            changed=result._result.get('changed', False),
            failed=result._result.get('failed', False),
            skipped=result._result.get('skipped', False),
            unreachable=result._result.get('unreachable', False),
            ignore_errors=kwargs.get('ignore_errors', False),
        )

    @commit()
    def log_stats(self, stats):
        '''Logs playbook statistics to the database.'''
        LOG.debug('logging stats')
        hosts = sorted(stats.processed.keys())
        for hostname in hosts:
            host = self.get_or_create_host(hostname)
            host_stats = stats.summarize(hostname)
            db.session.add(models.Stats(
                playbook=self.playbook,
                host=host,
                changed=host_stats['changed'],
                unreachable=host_stats['unreachable'],
                failed=host_stats['failures'],
                ok=host_stats['ok'],
                skipped=host_stats['skipped']
            ))

    def close_task(self):
        '''Marks the completion time of the currently active task.'''
        if self.task is not None:
            LOG.debug('closing task %s (%s)', self.task.name, self.task.id)
            self.task.stop()
            db.session.add(self.task)
            db.session.commit()

            self.task = None

    def close_play(self):
        '''Marks the completion time of the currently active play.'''
        if self.play is not None:
            LOG.debug('closing play %s (%s)', self.play.name, self.play.id)
            self.play.stop()
            db.session.add(self.play)
            db.session.commit()

            self.play = None

    def close_playbook(self):
        '''Marks the completion time of the currently active playbook.'''
        if self.playbook is not None:
            LOG.debug('closing playbook %s', self.playbook.path)
            self.playbook.stop()
            db.session.add(self.playbook)
            db.session.commit()

    def v2_runner_on_ok(self, result, **kwargs):
        self.log_task(result, 'ok', **kwargs)

    def v2_runner_on_unreachable(self, result, **kwargs):
        self.log_task(result, 'unreachable', **kwargs)

    def v2_runner_on_failed(self, result, **kwargs):
        self.log_task(result, 'failed', **kwargs)

    def v2_runner_on_skipped(self, result, **kwargs):
        self.log_task(result, 'skipped', **kwargs)

    @commit('task')
    def v2_playbook_on_task_start(self, task, is_conditional,
                                  is_handler=False):
        self.close_task()

        LOG.debug('starting task %s (action %s)',
                  task.name, task.action)
        pathspec = task.get_path()
        if pathspec:
            path, lineno = pathspec.split(':', 1)
            lineno = int(lineno)
        else:
            path = None
            lineno = None

        self.task = models.Task(
            name=task.name,
            sortkey=next(self.task_counter),
            action=task.action,
            play=self.play,
            playbook=self.playbook,
            path=path,
            lineno=lineno,
            is_handler=is_handler)

        self.task.start()

    def v2_playbook_on_handler_task_start(self, task):
        self.v2_playbook_on_task_start(task, False, is_handler=True)

    @commit('playbook')
    def v2_playbook_on_start(self, playbook):
        LOG.debug('starting playbook %s', playbook._file_name)
        self.playbook = models.Playbook(
            path=playbook._file_name,
        )

        self.playbook.start()

    @commit('play')
    def v2_playbook_on_play_start(self, play):
        self.close_task()
        self.close_play()

        LOG.debug('starting play %s', play.name)
        if self.play is not None:
            self.play.stop()

        self.play = models.Play(
            name=play.name,
            sortkey=next(self.play_counter),
            playbook=self.playbook
        )

        self.play.start()

    def v2_playbook_on_stats(self, stats):
        self.close_task()
        self.close_play()
        self.close_playbook()

        self.log_stats(stats)

        LOG.debug('closing database')
        db.session.close()

    def v2_playbook_on_include(self, included_file):
        for host in included_file._hosts:
            LOG.debug('log include file for host %s', host)
            self.log_task(IncludeResult(host, included_file._filename), 'ok')
