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
import zlib
import hashlib
import functools
from datetime import datetime, timedelta

# This makes all the exceptions available as "models.<exception_name>".
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import *  # NOQA
import sqlalchemy.types as types

db = SQLAlchemy()


def mkuuid():
    '''This used to generate primary keys in the database tables.  We were
    simply passing `default=uuid.uuid4` to `db.Column`, but it turns out
    that while some database drivers seem to implicitly call `str()`,
    others may be calling `repr()` which resulted in SQLIte trying to
    use keys like `UUID('a496d538-c819-4f7c-8926-e3abe317239d')`.'''

    return str(uuid.uuid4())


def content_sha1(context):
    '''Used by the FileContent class to automatically compute the sha1
    hash of content before storing it to the database.'''
    return hashlib.sha1(context.current_parameters['content']).hexdigest()


# Primary key columns are of these type.
pkey_type = db.String(36)

# This defines the standard primary key column used in our tables.
std_pkey = functools.partial(
    db.Column, pkey_type, primary_key=True,
    nullable=False, default=mkuuid)

# Common options for one-to-one relationships in our database.
one_to_one = functools.partial(
    db.relationship, passive_deletes=False,
    cascade='all, delete-orphan', uselist=False)

# common options for one-to-many relationships in our database.
one_to_many = functools.partial(
    db.relationship, passive_deletes=False,
    cascade='all, delete-orphan', lazy='dynamic')

# common options for many-to-one relationships in our database.
many_to_one = functools.partial(
    db.relationship, passive_deletes=False,
    cascade='all, delete-orphan',
    single_parent=True)

# Common options for many-to-many relationships in our database.
many_to_many = functools.partial(
    db.relationship, passive_deletes=False,
    cascade='all, delete',
    lazy='dynamic')


# Common options for foreign key relationships.
def std_fkey(col):
    return db.Column(pkey_type,
                     db.ForeignKey(col, ondelete='RESTRICT'))


class TimedEntity(object):
    @property
    def duration(self):
        '''Calculate `(time_end-time_start)` and return the resulting
        `datetime.timedelta` object.'''

        if self.time_end is None or self.time_start is None:
            return timedelta(seconds=0)
        else:
            return self.time_end - self.time_start

    def start(self):
        '''Explicitly set `self.time_start`.'''
        self.time_start = datetime.now()

    def stop(self):
        '''Explicitly set `self.time_end`.'''
        self.time_end = datetime.now()


class CompressedText(types.TypeDecorator):
    '''Implements a new sqlalchemy column type that automatically
    compresses data when writing it to the database and decompresses
    the data when reading it.

    http://docs.sqlalchemy.org/en/latest/core/custom_types.html'''

    impl = types.Binary

    def process_bind_param(self, value, dialect):
        return zlib.compress(value if value else '')

    def process_result_value(self, value, dialect):
        return zlib.decompress(value)

    def copy(self, **kwargs):
        return CompressedText(self.impl.length)


class Playbook(db.Model, TimedEntity):
    '''The `Playbook` class represents a single run of
    `ansible-playbook`.

    `Playbook` entities have the following relationships:

    - `plays` -- a list of plays encountered in this playbook run.
    - `tasks` -- a list of tasks encountered in this playbook run.
    - `stats` -- a list of  statistic records, one for each host
      involved in this playbook.
    - `hosts` -- a list of hosts involved in this playbook
    - `files` -- a list of files encountered by this playbook
      (via include or role directives).
    '''

    __tablename__ = 'playbooks'

    id = std_pkey()
    path = db.Column(db.Text)
    files = one_to_many('File', backref='playbook')
    plays = one_to_many('Play', backref='playbook')
    tasks = one_to_many('Task', backref='playbook')
    stats = one_to_many('Stats', backref='playbook')
    hosts = one_to_many('Host', backref='playbook')

    time_start = db.Column(db.DateTime, default=datetime.now)
    time_end = db.Column(db.DateTime)

    complete = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Playbook %s>' % self.path


class File(db.Model):
    '''Represents a task list (role or playbook or included file)
    referenced by an Ansible run.'''

    __tablename__ = 'files'
    __table_args__ = (
        db.UniqueConstraint('playbook_id', 'path'),
    )

    id = std_pkey()
    playbook_id = std_fkey('playbooks.id')

    # This has to be a String intead of Text because of
    # http://stackoverflow.com/questions/1827063/
    # and it must have a max length smaller than PATH_MAX because MySQL is
    # limited to a maximum key length of 3072 bytes.  This
    # restrictions stems from the fact that we are using this column in
    # a UNIQUE constraint.
    path = db.Column(db.String(3000))
    content = many_to_one('FileContent', backref='files')
    content_id = db.Column(db.String(40),
                           db.ForeignKey('file_contents.id'))

    # is_playbook is true for playbooks referenced directly on the
    # ansible-playbook command line.
    is_playbook = db.Column(db.Boolean, default=False)


class FileContent(db.Model):
    '''Stores content of Ansible task lists encountered during an
    Ansible run.  We store content keyed by the its sha1 hash, so if a
    file doesn't change the content will only be stored once in the
    database.  The hash is calculated automatically when the object is
    written to the database.'''

    __tablename__ = 'file_contents'

    id = db.Column(db.String(40), primary_key=True, default=content_sha1)
    content = db.Column(CompressedText((2**32) - 1))


class Play(db.Model, TimedEntity):
    '''The `Play` class represents a play in an ansible playbook.

    `Play` entities have the following relationships:

    - `tasks` -- a list of tasks in this play
    - `task_results` -- a list of task results in this play (via the
      `tasks` relationship defined by `TaskResult`).
    '''

    __tablename__ = 'plays'

    id = std_pkey()
    playbook_id = std_fkey('playbooks.id')
    name = db.Column(db.Text)
    sortkey = db.Column(db.Integer)
    tasks = one_to_many('Task', backref='play')

    time_start = db.Column(db.DateTime, default=datetime.now)
    time_end = db.Column(db.DateTime)

    def __repr__(self):
        return '<Play %s>' % (self.name or self.id)

    @property
    def offset_from_playbook(self):
        return self.time_start - self.playbook.time_start


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

    id = std_pkey()
    playbook_id = std_fkey('playbooks.id')
    play_id = std_fkey('plays.id')

    name = db.Column(db.Text)
    sortkey = db.Column(db.Integer)
    action = db.Column(db.Text)
    is_handler = db.Column(db.Boolean)

    file = many_to_one('File', backref='tasks')
    file_id = std_fkey('files.id')
    lineno = db.Column(db.Integer)

    time_start = db.Column(db.DateTime, default=datetime.now)
    time_end = db.Column(db.DateTime)

    task_results = one_to_many('TaskResult', backref='task')

    def __repr__(self):
        return '<Task %s>' % (self.name or self.id)

    @property
    def offset_from_playbook(self):
        return self.time_start - self.playbook.time_start

    @property
    def offset_from_play(self):
        return self.time_start - self.play.time_start


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

    id = std_pkey()
    task_id = std_fkey('tasks.id')
    host_id = std_fkey('hosts.id')

    status = db.Column(db.Enum('ok', 'failed', 'skipped', 'unreachable'))
    changed = db.Column(db.Boolean, default=False)
    failed = db.Column(db.Boolean, default=False)
    skipped = db.Column(db.Boolean, default=False)
    unreachable = db.Column(db.Boolean, default=False)
    ignore_errors = db.Column(db.Boolean, default=False)
    result = db.Column(CompressedText((2**32) - 1))

    time_start = db.Column(db.DateTime, default=datetime.now)
    time_end = db.Column(db.DateTime)

    @property
    def derived_status(self):
        if self.status == 'ok' and self.changed:
            return 'changed'
        elif self.status == 'failed' and self.ignore_errors:
            return 'ignored'
        else:
            return self.status

    def __repr__(self):
        return '<TaskResult %s>' % self.host.name


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
    __table_args__ = (
        db.UniqueConstraint('playbook_id', 'name'),
    )

    id = std_pkey()
    playbook_id = std_fkey('playbooks.id')
    name = db.Column(db.String(255), index=True)

    facts = one_to_one('HostFacts', backref='host')
    task_results = one_to_many('TaskResult', backref='host')
    stats = one_to_one('Stats', backref='host')

    def __repr__(self):
        return '<Host %s>' % self.name


class HostFacts(db.Model):
    '''The `HostFacts` object represents a host reference by an Ansible
    inventory. It is meant to record facts when a setup task is run for a host.

    A `HostFacts` entity has the following relationship:

    - `hosts` -- the host owner of the facts
    '''

    __tablename__ = 'host_facts'

    id = std_pkey()
    host_id = std_fkey('hosts.id')
    timestamp = db.Column(db.DateTime, default=datetime.now)
    values = db.Column(db.Text(16777215))

    def __repr__(self):
        return '<HostFacts %s>' % self.host.name


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

    id = std_pkey()
    playbook_id = std_fkey('playbooks.id')
    host_id = std_fkey('hosts.id')

    changed = db.Column(db.Integer, default=0)
    failed = db.Column(db.Integer, default=0)
    ok = db.Column(db.Integer, default=0)
    skipped = db.Column(db.Integer, default=0)
    unreachable = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<Stats for %s>' % self.host.name
