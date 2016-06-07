import json
import random

import ara.models as m
from ara.models import db


def ansible_run(complete=True, gather_facts=True):
    '''Simulate a simple Ansible run by creating the
    expected database objects.  This roughly approximates the
    following playbook:

        - hosts: host-<int>
          gather_facts: true
          tasks:
            - test-action:

    Where `<int>` is a random integer generated each time this
    function is called.

    Set the `complete` parameter to `False` to simulate an
    aborted Ansible run.
    Set the `gathered_facts` parameter to `False` to simulate a run with no
    facts gathered.
    '''

    playbook = m.Playbook(path='testing.yml')
    play = m.Play(playbook=playbook, name='test play')
    task = m.Task(play=play, playbook=playbook,
                  action='test-action')
    host = m.Host(name='host-%04d' % random.randint(0, 9999),
                  playbook=playbook)
    result = m.TaskResult(task=task, status='ok', host=host,
                          result='this is a test')

    ctx = dict(
        playbook=playbook,
        play=play,
        task=task,
        host=host,
        result=result)

    if gather_facts:
        facts = m.HostFacts(host=host, values='{"fact": "value"}')
        ctx['facts'] = facts

    for obj in ctx.values():
        if hasattr(obj, 'start'):
            obj.start()
        db.session.add(obj)

    db.session.commit()

    if complete:
        stats = m.Stats(playbook=playbook, host=host)
        ctx['stats'] = stats
        db.session.add(stats)
        ctx['playbook'].complete = True

        for obj in ctx.values():
            if hasattr(obj, 'stop'):
                obj.stop()

    db.session.commit()

    return ctx
