#  Copyright (c) 2017 Red Hat, Inc.
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

import decorator
import logging
import os
import six

from ansible import __version__ as ansible_version
from ansible.plugins.callback import CallbackBase
from ara.api.files import FileApi
from ara.api.hosts import HostApi
from ara.api.plays import PlayApi
from ara.api.playbooks import PlaybookApi
from ara.api.results import ResultApi
from ara.api.tasks import TaskApi
from ara.db.models import db
from ara.webapp import create_app
from datetime import datetime
from flask import current_app
from oslo_serialization import jsonutils
from oslo_utils import encodeutils

# To retrieve Ansible CLI options
try:
    from __main__ import cli
except ImportError:
    cli = None

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
        return super(CommitAfter, kls).__new__(kls, name, bases, attrs)


@six.add_metaclass(CommitAfter)
class CallbackModule(CallbackBase):
    """
    Saves data from an Ansible run into a database
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'ara'

    def __init__(self):
        super(CallbackModule, self).__init__()

        if not current_app:
            ctx = app.app_context()
            ctx.push()

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

    def v2_runner_item_on_ok(self, result):
        self.loop_items.append(result)

    def v2_runner_item_on_failed(self, result):
        self.loop_items.append(result)

    def v2_runner_item_on_skipped(self, result):
        self.loop_items.append(result)

    def v2_runner_retry(self, result):
        self.loop_items.append(result)

    def v2_runner_on_ok(self, result, **kwargs):
        self._log_task(result, 'ok', **kwargs)

    def v2_runner_on_unreachable(self, result, **kwargs):
        self._log_task(result, 'unreachable', **kwargs)

    def v2_runner_on_failed(self, result, **kwargs):
        self._log_task(result, 'failed', **kwargs)

    def v2_runner_on_skipped(self, result, **kwargs):
        self._log_task(result, 'skipped', **kwargs)

    def v2_playbook_on_task_start(self, task, is_conditional, handler=False):
        self._close_task()

        LOG.debug('Starting task %s (action %s)',
                  task.get_name(),
                  task.action)
        pathspec = task.get_path()
        if pathspec:
            path, lineno = pathspec.split(':', 1)
            lineno = int(lineno)
        else:
            path = self.playbook['path']
            lineno = 1
        # Ensure this task's file was added to the playbook -- files that are
        # dynamically included do not show up in the playbook or play context
        self._create_files(self.playbook['id'], [path])

        # TODO: Implement a one() method for retrieving one or raise exception
        file_ = FileApi().get(playbook_id=self.playbook['id'],
                              path=path)
        file_ = jsonutils.loads(file_.data)[0]

        # TODO: Wrap this validation logic
        response = TaskApi().post(dict(
            name=task.get_name(),
            action=task.action,
            play_id=self.play['id'],
            playbook_id=self.playbook['id'],
            file_id=file_['id'],
            tags=task._attributes['tags'],
            lineno=lineno,
            handler=handler
        ))
        if response.status_code not in [200, 201]:
            raise SystemError("HTTP {0} when posting data: {1}".format(
                response.status_code, response.data
            ))
        self.task = jsonutils.loads(response.data)

        return self.task

    def v2_playbook_on_handler_task_start(self, task):
        self.v2_playbook_on_task_start(task, False, handler=True)

    def v2_playbook_on_start(self, playbook):
        path = os.path.abspath(playbook._file_name)
        if self._options is not None:
            parameters = self._options.__dict__.copy()
        else:
            parameters = {}

        # Potentially sanitize some user-specified keys
        for parameter in app.config['ARA_IGNORE_PARAMETERS']:
            if parameter in parameters:
                msg = "Parameter not saved by ARA due to configuration"
                parameters[parameter] = msg

        LOG.debug('starting playbook %s', path)

        # TODO: Wrap this validation logic
        response = PlaybookApi().post(dict(
            ansible_version=ansible_version,
            path=path,
            parameters=parameters,
        ))
        if response.status_code not in [200, 201]:
            raise SystemError("HTTP {0} when posting data: {1}".format(
                response.status_code, response.data
            ))
        self.playbook = jsonutils.loads(response.data)

        # Record all the files involved in the playbook
        files = playbook._loader._FILE_CACHE.keys()
        self._create_files(self.playbook['id'], files)

        # Cache the playbook data in memory for ara_record/ara_read
        current_app._cache['playbook'] = self.playbook

        return self.playbook

    def v2_playbook_on_play_start(self, play):
        self._close_task()
        self._close_play()

        LOG.debug('Starting play %s', play.name)

        # Record all the files involved in the play
        files = play._loader._FILE_CACHE.keys()
        self._create_files(self.playbook['id'], files)

        # Record all the hosts involved in the play
        hosts = play._variable_manager._inventory._restriction
        self._create_hosts(self.playbook['id'], hosts)

        # TODO: Wrap this validation logic
        response = PlayApi().post(dict(
            name=play.name,
            playbook_id=self.playbook['id'],
        ))
        if response.status_code not in [200, 201]:
            raise SystemError("HTTP {0} when posting data: {1}".format(
                response.status_code, response.data
            ))
        self.play = jsonutils.loads(response.data)

        return self.play

    def v2_playbook_on_stats(self, stats):
        LOG.debug('Logging stats')
        hosts = sorted(stats.processed.keys())
        for hostname in hosts:
            # TODO: Implement a one() method for retrieving one or raise
            # exception
            host = HostApi().get(playbook_id=self.playbook['id'],
                                 name=encodeutils.safe_encode(hostname))
            host = jsonutils.loads(host.data)[0]
            host_stats = stats.summarize(hostname)

            # TODO: Add validation for this
            HostApi().patch(dict(
                id=host['id'],
                changed=host_stats['changed'],
                failed=host_stats['failures'],
                ok=host_stats['ok'],
                skipped=host_stats['skipped'],
                unreachable=host_stats['unreachable']
            ))

        self._close_task()
        self._close_play()
        self._close_playbook()

    def _log_task(self, result, status, **kwargs):
        """
        'log_task' is called when an individual task instance on a single
        host completes. It is responsible for logging a single
        'Result' record to the database.
        """
        LOG.debug('Logging task result for task %s (%s), Host: %s',
                  self.task['name'], self.task['id'], result._host.get_name())

        ended = datetime.utcnow().isoformat()

        # TODO: Implement a one() method for retrieving one or raise exception
        host = HostApi().get(playbook_id=self.playbook['id'],
                             name=result._host.get_name())
        host = jsonutils.loads(host.data)[0]

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
            results = jsonutils.loads(jsonutils.dumps(results))
        else:
            results = jsonutils.loads(self._dump_results(result._result))

        # TODO: Wrap this validation logic
        response = ResultApi().post(dict(
            playbook_id=self.playbook['id'],
            play_id=self.play['id'],
            task_id=self.task['id'],
            host_id=host['id'],
            started=self.task['started'],
            ended=ended,
            result=results,
            status=status,
            changed=result._result.get('changed', False),
            failed=result._result.get('failed', False),
            skipped=result._result.get('skipped', False),
            unreachable=result._result.get('unreachable', False),
            ignore_errors=kwargs.get('ignore_errors', False),
        ))
        if response.status_code not in [200, 201]:
            raise SystemError("HTTP {0} when posting data: {1}".format(
                response.status_code, response.data
            ))

        # TODO: Abstract this under the API
        if self.task['action'] == 'setup' and 'ansible_facts' in results:
            # TODO: Add validation for this
            HostApi().patch(dict(
                id=host['id'],
                facts=results['ansible_facts']
            ))

    def _close_task(self):
        """
        Marks the completion time of the currently active task.
        """
        if self.task is not None:
            LOG.debug('Closing task %s (%s)',
                      self.task['name'],
                      self.task['id'])

            # TODO: Add validation for this
            TaskApi().patch(dict(
                id=self.task['id'],
                ended=datetime.utcnow().isoformat()
            ))

            self.task = None
            self.loop_items = []

    def _close_play(self):
        """
        Marks the completion time of the currently active play.
        """
        if self.play is not None:
            LOG.debug('Closing play %s (%s)',
                      self.play['name'],
                      self.play['id'])

            # TODO: Add validation for this
            PlayApi().patch(dict(
                id=self.play['id'],
                ended=datetime.utcnow().isoformat()
            ))
            self.play = None

    def _close_playbook(self):
        """
        Marks the completion time of the currently active playbook.
        """
        if self.playbook is not None:
            LOG.debug('Closing playbook %s (%s)',
                      self.playbook['path'],
                      self.playbook['id'])

            # TODO: Add validation for this
            PlaybookApi().patch(dict(
                id=self.playbook['id'],
                ended=datetime.utcnow().isoformat(),
                completed=True
            ))

        db.session.close()

    def _create_hosts(self, playbook_id, hosts):
        """
        Ensures a list of hosts ("hosts") is added to "playbook_id"
        """
        current_hosts = []
        current = HostApi().get(playbook_id=playbook_id)
        if current.status_code == 200:
            # 404 means there are no hosts (yet)
            current = jsonutils.loads(current.data)
            current_hosts = [host['name'] for host in current]

        for host in hosts:
            if host not in current_hosts:
                # TODO: Wrap this validation logic
                response = HostApi().post(dict(
                    playbook_id=playbook_id,
                    name=host,
                ))
                if response.status_code not in [200, 201]:
                    raise SystemError("HTTP {0} when posting data: {1}".format(
                        response.status_code, response.data
                    ))

    def _create_files(self, playbook_id, files):
        """
        Ensures a list of files ("files") is added to "playbook_id"
        """
        current_files = []
        current = FileApi().get(playbook_id=playbook_id)
        if current.status_code == 200:
            # 404 means there are no files (yet)
            current = jsonutils.loads(current.data)
            current_files = [file_['path'] for file_ in current]

        for file_ in files:
            if file_ not in current_files:
                content = self._read_file(file_)
                response = FileApi().post(dict(
                    playbook_id=playbook_id,
                    path=file_,
                    content=content,
                ))
                if response.status_code not in [200, 201]:
                    raise SystemError(
                        "HTTP {0} when posting data: {1}".format(
                            response.status_code, response.data
                        ))
        return True

    def _read_file(self, path):
        try:
            with open(path, 'r') as fd:
                content = fd.read()
        except IOError as e:
            LOG.error("Unable to open {0} for reading: {1}".format(
                path, six.text_type(e)
            ))
            content = """ARA was not able to read this file successfully.
                      Refer to the logs for more information"""
        return content
