#   Copyright 2017 Red Hat, Inc. All Rights Reserved.
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

import decorator
import flask
import hashlib
import itertools
import logging
import os
from datetime import datetime

from ara import models
from ara.models import db
from ara.webapp import create_app

from ansible import __version__ as ansible_version
from ansible.plugins.callback import CallbackBase
import json

__metaclass__ = type

LOG = logging.getLogger('ara.callback')
app = create_app()


class CommitAfter(type):
    def __new__(kls, name, bases, attrs):
        def commit_after(func):
            def _commit_after(func, *args, **kwargs):
                rval = func(*args, **kwargs)
                db.session.commit()
                return rval

            return decorator.decorate(func, _commit_after)

        for k, v in attrs.items():
            if callable(v) and not k.startswith('_'):
                attrs[k] = commit_after(v)
        return super(CommitAfter, kls).__new__(
            kls, name, bases, attrs)


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

    __metaclass__ = CommitAfter

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'ara'

    def __init__(self):
        super(CallbackModule, self).__init__()

        if not flask.current_app:
            ctx = app.app_context()
            ctx.push()

        self.taskresult = None
        self.task = None
        self.play = None
        self.playbook = None
        self.stats = None

        self.play_counter = itertools.count()
        self.task_counter = itertools.count()

    def get_or_create_host(self, hostname):
        try:
            host = (models.Host.query
                    .filter_by(name=hostname)
                    .filter_by(playbook_id=self.playbook.id)
                    .one())
        except models.NoResultFound:
            host = models.Host(name=hostname, playbook=self.playbook)
            db.session.add(host)

        return host

    def get_or_create_file(self, path):
        try:
            if self.playbook.id:
                file_ = (models.File.query
                         .filter_by(path=path)
                         .filter_by(playbook_id=self.playbook.id)
                         .one())

                return file_
        except models.NoResultFound:
            pass

        file_ = models.File(path=path, playbook=self.playbook)
        db.session.add(file_)

        try:
            with open(path, 'r') as fd:
                data = fd.read()

            sha1 = hashlib.sha1(data).hexdigest()
            content = models.FileContent.query.get(sha1)

            if content is None:
                content = models.FileContent(content=data)

            file_.content = content
        except IOError:
            LOG.warn('failed to open %s for reading', path)

        return file_

    def log_task(self, result, status, **kwargs):
        '''`log_task` is called when an individual task instance on a single
        host completes. It is responsible for logging a single
        `TaskResult` record to the database.'''
        LOG.debug('logging task result for task %s (%s), host %s',
                  self.task.name, self.task.id, result._host.name)

        result.task_start = self.task.time_start
        result.task_end = datetime.now()
        host = self.get_or_create_host(result._host.name)

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

        db.session.add(self.taskresult)

        if self.task.action == 'setup' and 'ansible_facts' in result._result:
            values = json.dumps(result._result['ansible_facts'])
            facts = models.HostFacts(values=values)
            host.facts = facts

            db.session.add(facts)

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

            self.task = None

    def close_play(self):
        '''Marks the completion time of the currently active play.'''
        if self.play is not None:
            LOG.debug('closing play %s (%s)', self.play.name, self.play.id)
            self.play.stop()
            db.session.add(self.play)

            self.play = None

    def close_playbook(self):
        '''Marks the completion time of the currently active playbook.'''
        if self.playbook is not None:
            LOG.debug('closing playbook %s', self.playbook.path)
            self.playbook.stop()
            self.playbook.complete = True
            db.session.add(self.playbook)

    def v2_runner_on_ok(self, result, **kwargs):
        self.log_task(result, 'ok', **kwargs)

    def v2_runner_on_unreachable(self, result, **kwargs):
        self.log_task(result, 'unreachable', **kwargs)

    def v2_runner_on_failed(self, result, **kwargs):
        self.log_task(result, 'failed', **kwargs)

    def v2_runner_on_skipped(self, result, **kwargs):
        self.log_task(result, 'skipped', **kwargs)

    def v2_playbook_on_task_start(self, task, is_conditional,
                                  is_handler=False):
        self.close_task()

        LOG.debug('starting task %s (action %s)',
                  task.name, task.action)
        pathspec = task.get_path()
        if pathspec:
            path, lineno = pathspec.split(':', 1)
            lineno = int(lineno)
            file_ = self.get_or_create_file(path)
        else:
            path = None
            lineno = None
            file_ = None

        self.task = models.Task(
            name=task.name,
            sortkey=next(self.task_counter),
            action=task.action,
            play=self.play,
            playbook=self.playbook,
            file=file_,
            lineno=lineno,
            is_handler=is_handler)

        self.task.start()
        db.session.add(self.task)

    def v2_playbook_on_handler_task_start(self, task):
        self.v2_playbook_on_task_start(task, False, is_handler=True)

    def v2_playbook_on_start(self, playbook):
        path = os.path.abspath(playbook._file_name)

        LOG.debug('starting playbook %s', path)
        self.playbook = models.Playbook(
            ansible_version=ansible_version,
            path=path
        )

        self.playbook.start()
        db.session.add(self.playbook)

        file_ = self.get_or_create_file(path)
        file_.is_playbook = True

        # We need to persist the playbook id so it can be used by the modules
        data = {
            'playbook': {
                'id': self.playbook.id
            }
        }
        tmpfile = os.path.join(app.config['ARA_TMP_DIR'], 'ara.json')
        with open(tmpfile, 'w') as file:
            file.write(json.dumps(data))

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
        db.session.add(self.play)

    def v2_playbook_on_stats(self, stats):
        self.log_stats(stats)

        self.close_task()
        self.close_play()
        self.close_playbook()

        LOG.debug('closing database')
        db.session.close()

    def v2_playbook_on_include(self, included_file):
        for host in included_file._hosts:
            LOG.debug('log include file for host %s', host)
            self.log_task(IncludeResult(host, included_file._filename), 'ok')
