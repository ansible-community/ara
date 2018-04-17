#  Copyright (c) 2018 Red Hat, Inc.
#
#  This file is part of ARA Records Ansible.
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

import unittest

import ara.webapp as w
import ara.models as m
from ara.models import db

from ara.tests.unit import fakes


class TestAra(unittest.TestCase):
    """
    Common setup/teardown for ARA tests
    """
    def setUp(self):
        # TODO: Fix this, it's not used in create_app() and makes the databases
        # live on the filesystem rather than memory.
        self.config = {
            'SQLALCHEMY_DATABASE_URI': 'sqlite://',
            'TESTING': True
        }

        self.app = w.create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

        m.db.create_all()

    def tearDown(self):
        m.db.session.remove()
        m.db.drop_all()

        self.app_context.pop()


def ansible_run(complete=True, failed=False, gather_facts=True,
                ara_record=False):
    """
    Simulates an Ansible run by creating the expected database objects.
    This roughly approximates the following playbook:

        ---
        - name: ARA unit tests
          hosts: host-<random>
          gather_facts: yes
          tasks:
            - name: Fake task
              include: some/path/main.yml

            - name: Record something
              ara_record:
                key: 'test key'
                value: 'test value'
              when: ara_record

            - name: Fail something
              fail:
              when: failed

    Where '<random>' is a random integer generated each time.

    Set the 'complete' parameter to 'False' to simulate an aborted Ansible run.
    Set the 'failed' parameter to 'True' to simulate a failed Ansible run.
    Set the 'gathered_facts' parameter to 'False' to simulate a run with no
    facts gathered.
    Set the 'ara_record' parameter to 'True' to simulate a run with an
    ara_record task.
    """
    playbook = fakes.Playbook(complete=complete, path='/playbook.yml').model
    pb_file = fakes.File(playbook=playbook,
                         is_playbook=True,
                         path=playbook.path).model
    pb_content = fakes.FileContent(content=fakes.FAKE_PLAYBOOK_CONTENT).model

    play = fakes.Play(playbook=playbook).model
    host = fakes.Host(playbook=playbook).model

    tasks = []
    task_results = []

    task_file = fakes.File(playbook=playbook,
                           is_playbook=False,
                           path='/some/path/main.yml').model
    task_content = fakes.FileContent(content=fakes.FAKE_TASK_CONTENT).model
    task = fakes.Task(play=play,
                      playbook=playbook,
                      action='fake_action',
                      file=task_file,
                      file_id=task_file.id).model
    tasks.append(task)
    task_result = fakes.TaskResult(task=task,
                                   host=host,
                                   status='ok',
                                   changed=True,
                                   result='fake action result').model
    task_results.append(task_result)

    record_task = fakes.Task(play=play,
                             playbook=playbook,
                             action='ara_record',
                             file=task_file,
                             file_id=task_file.id).model
    tasks.append(record_task)

    ctx = dict(
        playbook=playbook,
        pb_file=pb_file,
        pb_content=pb_content,
        play=play,
        host=host,
        task=task,
        task_file=task_file,
        task_content=task_content,
        result=task_result,
    )

    items = [playbook, pb_file, pb_content,
             task_file, task_content, play, host]

    skipped = False
    if ara_record:
        msg = 'Data recorded in ARA for this playbook.'
        record_result = fakes.TaskResult(task=record_task,
                                         host=host,
                                         status='ok',
                                         changed=True,
                                         skipped=skipped,
                                         result=msg).model

        data = fakes.Data(playbook=playbook).model
        ctx['data'] = data
        items.append(data)
    else:
        skipped = True
        msg = 'Conditional check failed'
        record_result = fakes.TaskResult(task=record_task,
                                         host=host,
                                         status='skipped',
                                         changed=False,
                                         skipped=skipped,
                                         result=msg).model
    task_results.append(record_result)

    failed_task = fakes.Task(play=play,
                             playbook=playbook,
                             action='fail',
                             file=task_file,
                             file_id=task_file.id).model
    tasks.append(failed_task)
    if failed:
        msg = 'FAILED!'
        failed_result = fakes.TaskResult(task=failed_task,
                                         host=host,
                                         status='failed',
                                         changed=False,
                                         failed=True,
                                         result=msg).model
    else:
        skipped = True
        msg = 'Conditional check failed'
        failed_result = fakes.TaskResult(task=failed_task,
                                         host=host,
                                         status='skipped',
                                         changed=False,
                                         skipped=skipped,
                                         result=msg).model
    task_results.append(failed_result)

    if gather_facts:
        facts = fakes.HostFacts(host=host).model
        ctx['facts'] = facts
        items.append(facts)

    for item in items + tasks + task_results:
        if hasattr(item, 'start'):
            item.start()

    if complete:
        stats = fakes.Stats(playbook=playbook,
                            host=host,
                            ok=1,
                            skipped=int(skipped),
                            failed=int(failed)).model
        ctx['stats'] = stats
        items.append(stats)

        for item in items + tasks + task_results:
            if hasattr(item, 'stop'):
                item.stop()

    for item in items + tasks + task_results:
        db.session.add(item)
    db.session.commit()

    return ctx
