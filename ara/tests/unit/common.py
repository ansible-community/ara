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

import flask
import unittest

import ara.webapp as w
import ara.models as m
from ara.models import db

from ara.tests.unit import fakes


class TestAra(unittest.TestCase):
    '''Common setup/teardown for ARA tests'''
    def setUp(self):
        self.config = {
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "TESTING": True
        }

        self.app = w.create_app(self)
        self.client = self.app.test_client()

        if not flask.current_app:
            ctx = self.app.app_context()
            ctx.push()

        m.db.create_all()

    def tearDown(self):
        m.db.session.remove()
        m.db.drop_all()


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
    playbook = fakes.Playbook(complete=complete, path='playbook.yml').model
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
                           path='some/path/main.yml').model
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
                             action='ara_record').model
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
                                         skipped=True,
                                         result=msg).model
    task_results.append(record_result)

    failed_task = fakes.Task(play=play,
                             playbook=playbook,
                             action='fail').model
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
                                         skipped=True,
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
