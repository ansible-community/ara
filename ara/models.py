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

import uuid
from datetime import datetime
# This makes all the exceptions available as "models.<exception_name>".
from sqlalchemy.orm.exc import *  # NOQA

from ara import db


def mkuuid():
    '''This used to generate primary keys in the database tables.  We were
    simply passing `default=uuid.uuid4` to `db.Column`, but it turns out
    that while some database drivers seem to implicitly call `str()`,
    others may be calling `repr()` which resulted in SQLIte trying to
    use keys like `UUID('a496d538-c819-4f7c-8926-e3abe317239d')`.'''

    return str(uuid.uuid4())


class TimedEntity(object):
    @property
    def duration(self):
        '''Calculate `(time_end-time_start)` and return the resulting
        `datetime.timedelta` object.'''

        return self.time_end - self.time_start

    def start(self):
        '''Explicitly set `self.time_start`.'''
        self.time_start = datetime.now()

    def stop(self):
        '''Explicitly set `self.time_end`.'''
        self.time_end = datetime.now()


class Playbook(db.Model, TimedEntity):
    '''The `Playbook` class represents a single run of
    `ansible-playbook`.

    `Playbook` entities have the following relationships:

    - `plays` -- a list of plays encountered in this playbook run.
    - `tasks` -- a list of tasks encountered in this playbook run.
    - `stats` -- a list of  statistic records, one for each host
      involved in this playbook.
    - `hosts` -- a list of hosts involved in this plabook (via the
      `playbooks` relationship defined by `Host` table).
    '''

    __tablename__ = 'playbooks'

    id = db.Column(db.String(36), primary_key=True, nullable=False,
                   default=mkuuid)
    path = db.Column(db.Text)
    plays = db.relationship('Play', backref='playbook', lazy='dynamic')
    tasks = db.relationship('Task', backref='playbook', lazy='dynamic')
    stats = db.relationship('Stats', backref='playbook', lazy='dynamic')

    time_start = db.Column(db.DateTime, default=datetime.now)
    time_end = db.Column(db.DateTime)

    def __repr__(self):
        return '<Playbook %s>' % self.path


class Play(db.Model, TimedEntity):
    '''The `Play` class represents a play in an ansible playbook.

    `Play` entities have the following relationships:

    - `tasks` -- a list of tasks in this play
    - `task_results` -- a list of task results in this play (via the
      `tasks` relationship defined by `TaskResult`).
    '''

    __tablename__ = 'plays'

    id = db.Column(db.String(36), primary_key=True, nullable=False,
                   default=mkuuid)
    playbook_id = db.Column(db.String(36), db.ForeignKey('playbooks.id'))
    name = db.Column(db.Text)
    tasks = db.relationship('Task', backref='play', lazy='dynamic')

    time_start = db.Column(db.DateTime, default=datetime.now)
    time_end = db.Column(db.DateTime)

    def __repr__(self):
        return '<Play %s>' % (self.name or self.id)


class Task(db.Model, TimedEntity):
    '''The `Task` class represents a single task defined in an Ansible
    playbook.

    `Task` entities have the following relationships:

    - `playbook` -- the playbook containing thist ask (via the `tasks`
      relationship defined by `Playbook`)
    - `play` -- the play containing this task (via the `tasks`
       relationship defined by `Play`)
    - `task_results` -- a list of results for each host targeted by
      this task.
    '''

    __tablename__ = 'tasks'

    id = db.Column(db.String(36), primary_key=True, nullable=False,
                   default=mkuuid)
    playbook_id = db.Column(db.String(36), db.ForeignKey('playbooks.id'))
    play_id = db.Column(db.String(36), db.ForeignKey('plays.id'))

    name = db.Column(db.Text)
    action = db.Column(db.Text)
    path = db.Column(db.Text)
    lineno = db.Column(db.Integer)
    is_handler = db.Column(db.Boolean)

    time_start = db.Column(db.DateTime, default=datetime.now)
    time_end = db.Column(db.DateTime)

    task_results = db.relationship('TaskResult', backref='task',
                                   lazy='dynamic')

    def __repr__(self):
        return '<Task %s>' % (self.name or self.id)


class TaskResult(db.Model, TimedEntity):
    '''The `TaskResult` class represents the result of running a
    single task on a single host.

    A `TaskResult` entity has the following relationships:

    - `task` -- the task for which this is a result (via the
      `task_results` relationship defined by `Task`).
    - `host` -- the host associated with this result (via the
      `task_results` relationship defined by `Host`)
    '''

    __tablename__ = 'task_results'

    id = db.Column(db.String(36), primary_key=True, nullable=False,
                   default=mkuuid)
    task_id = db.Column(db.String(36), db.ForeignKey('tasks.id'))
    host_id = db.Column(db.String(36), db.ForeignKey('hosts.id'))

    changed = db.Column(db.Boolean)
    failed = db.Column(db.Boolean)
    skipped = db.Column(db.Boolean)
    unreachable = db.Column(db.Boolean)
    ignore_errors = db.Column(db.Boolean)
    result = db.Column(db.Text)

    time_start = db.Column(db.DateTime, default=datetime.now)
    time_end = db.Column(db.DateTime)

    def __repr__(self):
        return '<TaskResult %s>' % self.host.name


host_playbook = db.Table(
    'host_playbook',
    db.Column('host_id', db.String(36), db.ForeignKey('hosts.id')),
    db.Column('playbook_id', db.String(36), db.ForeignKey('playbooks.id')))


class Host(db.Model):
    '''The `Host` object represents a host reference by an Ansible
    inventory.

    A `Host` entity has the following relationships:

    - `task_results` -- a list of `TaskResult` objects associated with
      this host.
    - `stats` -- a list of `Stats` objects resulting from playbook
      runs against this host.
    - `playbooks` -- a list of `Playbook` runs that have included this
      host.
    '''

    __tablename__ = 'hosts'

    id = db.Column(db.String(36), primary_key=True, nullable=False,
                   default=mkuuid)
    name = db.Column(db.String(255), unique=True, index=True)

    task_results = db.relationship('TaskResult', backref='host',
                                   lazy='dynamic')
    stats = db.relationship('Stats', backref='host',
                            lazy='dynamic')
    playbooks = db.relationship('Playbook', secondary=host_playbook,
                                backref='hosts', lazy='dynamic')

    def __repr__(self):
        return '<Host %s>' % self.name


class Stats(db.Model):
    '''A `Stats` object contains statistics for a single host from a
    single Ansible playbook run.

    A `Stats` entity has the following relationships:

    - `playbook` -- the playbook associated with these statistics (via
      the `stats` relationship defined in `Playbook`)
    - `host` -- The host associated with these statistics (via the
      `stats` relationship defined in `Host`)
    '''

    __tablename__ = 'stats'

    id = db.Column(db.String(36), primary_key=True, nullable=False,
                   default=mkuuid)
    playbook_id = db.Column(db.String(36), db.ForeignKey('playbooks.id'))
    host_id = db.Column(db.String(36), db.ForeignKey('hosts.id'))

    changed = db.Column(db.Integer)
    failed = db.Column(db.Integer)
    ok = db.Column(db.Integer)
    skipped = db.Column(db.Integer)
    unreachable = db.Column(db.Integer)

    def __repr__(self):
        return '<Stats for %s>' % self.host.name
