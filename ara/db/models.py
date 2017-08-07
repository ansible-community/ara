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

import functools
import hashlib
import zlib

from datetime import datetime
from datetime import timedelta
from oslo_utils import encodeutils
from oslo_serialization import jsonutils

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declared_attr
# This makes all the exceptions available as "models.<exception_name>".
from sqlalchemy.orm.exc import *  # NOQA
from sqlalchemy.orm import backref
import sqlalchemy.types as types

metadata = MetaData(
    naming_convention={
        "ix": 'ix_%(column_0_label)s',
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(column_0_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
)
db = SQLAlchemy(metadata=metadata)


def content_sha1(context):
    """
    Used by the FileContent model to automatically compute the sha1
    hash of content before storing it to the database.
    """
    try:
        content = context.current_parameters['content']
    except AttributeError:
        content = context
    return hashlib.sha1(encodeutils.to_utf8(content)).hexdigest()


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


class TimedEntity(object):
    @property
    def duration(self):
        """
        Calculates '(time_end-time_start)' and return the resulting
        'datetime.timedelta' object.
        """
        if self.time_end is None or self.time_start is None:
            return timedelta(seconds=0)
        else:
            return self.time_end - self.time_start

    def start(self):
        """
        Explicitly sets 'self.time_start'
        """
        self.time_start = datetime.utcnow()

    def stop(self):
        """
        Explicitly sets 'self.time_end'
        """
        self.time_end = datetime.utcnow()


class CompressedData(types.TypeDecorator):
    """
    Implements a new sqlalchemy column type that automatically serializes
    and compresses data when writing it to the database and decompresses
    the data when reading it.

    http://docs.sqlalchemy.org/en/latest/core/custom_types.html
    """
    impl = types.Binary

    def process_bind_param(self, value, dialect):
        return zlib.compress(encodeutils.to_utf8(jsonutils.dumps(value)))

    def process_result_value(self, value, dialect):
        if value is not None:
            return jsonutils.loads(zlib.decompress(value))
        else:
            return value

    def copy(self, **kwargs):
        return CompressedData(self.impl.length)


class CompressedText(types.TypeDecorator):
    """
    Implements a new sqlalchemy column type that automatically compresses
    data when writing it to the database and decompresses the data when
    reading it.

    http://docs.sqlalchemy.org/en/latest/core/custom_types.html
    """
    impl = types.Binary

    def process_bind_param(self, value, dialect):
        return zlib.compress(encodeutils.to_utf8(value))

    def process_result_value(self, value, dialect):
        return encodeutils.safe_decode(zlib.decompress(value))

    def copy(self, **kwargs):
        return CompressedText(self.impl.length)


class PlaybookMixin(object):
    @declared_attr
    def playbook_id(cls):
        return db.Column(db.Integer, db.ForeignKey(Playbook.id))


class Base(db.Model, PlaybookMixin):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)


class Playbook(db.Model, TimedEntity):
    """
    The 'Playbook' class represents a single run of 'ansible-playbook'.

    'Playbook' entities have the following relationships:
    - 'data' -- a list of k/v pairs recorded in this playbook run
    - 'plays' -- a list of plays encountered in this playbook run
    - 'tasks' -- a list of tasks encountered in this playbook run
    - 'stats' -- a list of  statistic records, one for each host
      involved in this playbook
    - 'hosts' -- a list of hosts involved in this playbook
    - 'files' -- a list of files encountered by this playbook
      (via include or role directives).
    """
    __tablename__ = 'playbooks'
    files = one_to_many('File', backref='playbook')
    hosts = one_to_many('Host', backref='playbook')
    plays = one_to_many('Play', backref='playbook')
    records = one_to_many('Record', backref='playbook')
    results = one_to_many('Result', backref='playbook')
    stats = one_to_many('Stats', backref='playbook')
    tasks = one_to_many('Task', backref='playbook')

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(255))
    ansible_version = db.Column(db.String(255))
    parameters = db.Column(CompressedData((2 ** 32) - 1))
    complete = db.Column(db.Boolean, default=False)

    time_start = db.Column(db.DateTime, default=datetime.utcnow)
    time_end = db.Column(db.DateTime)

    @property
    def file(self):
        return (self.files
                .filter(File.playbook_id == self.id)
                .filter(File.is_playbook)).one()

    def __repr__(self):
        return '<Playbook %s>' % self.path


class File(Base):
    """
    Represents a task list (role or playbook or included file) referenced by
    an Ansible run.
    """
    __tablename__ = 'files'
    __table_args__ = (
        db.UniqueConstraint('playbook_id', 'path'),
    )
    content_id = db.Column(db.Integer, db.ForeignKey('file_contents.id'))
    content = many_to_one('FileContent', backref='files')
    tasks = many_to_one('Task', backref=backref('file', uselist=False))

    # This has to be a String instead of Text because of
    # http://stackoverflow.com/questions/1827063/
    # and it must have a max length smaller than PATH_MAX because MySQL is
    # limited to a maximum key length of 3072 bytes. These restrictions stem
    # from the fact that we are using this column in a UNIQUE constraint.
    path = db.Column(db.String(255))

    # is_playbook is true for playbooks referenced directly on the
    # ansible-playbook command line.
    is_playbook = db.Column(db.Boolean, default=False)


class FileContent(db.Model):
    """
    Stores content of Ansible task lists encountered during an Ansible run.
    We store content keyed by the its sha1 hash, so if a file doesn't change
    the content will only be stored once in the database. The hash is
    calculated automatically when the object is written to the database.
    """
    __tablename__ = 'file_contents'

    id = db.Column(db.Integer, primary_key=True)
    sha1 = db.Column(db.String(40), default=content_sha1, unique=True)
    content = db.Column(CompressedText((2**32) - 1))


class Play(Base, TimedEntity):
    """
    The 'Play' class represents a play in an ansible playbook.

    'Play' entities have the following relationships:
    - 'tasks' -- a list of tasks in this play
    - 'results' -- a list of task results in this play (via the
      'tasks' relationship defined by 'Result').
    """
    __tablename__ = 'plays'
    results = one_to_many('Result', backref='play')
    tasks = one_to_many('Task', backref='play')

    name = db.Column(db.Text)

    time_start = db.Column(db.DateTime, default=datetime.utcnow)
    time_end = db.Column(db.DateTime)

    def __repr__(self):
        return '<Play %s>' % (self.name or self.id)

    @property
    def offset_from_playbook(self):
        return self.time_start - self.playbook.time_start


class Task(Base, TimedEntity):
    """
    The 'Task' class represents a single task defined in an Ansible playbook.

    'Task' entities have the following relationships:
    - 'playbook' -- the playbook containing this task (via the 'tasks'
      relationship defined by 'Playbook')
    - 'play' -- the play containing this task (via the 'tasks' relationship
      defined by 'Play')
    - 'results' -- a list of results for each host targeted by this task.
    """
    __tablename__ = 'tasks'
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'))
    play_id = db.Column(db.Integer, db.ForeignKey('plays.id'))
    results = one_to_many('Result', backref='task')

    name = db.Column(db.Text)
    action = db.Column(db.Text)
    lineno = db.Column(db.Integer)
    tags = db.Column(db.Text)
    is_handler = db.Column(db.Boolean)

    time_start = db.Column(db.DateTime, default=datetime.utcnow)
    time_end = db.Column(db.DateTime)

    def __repr__(self):
        return '<Task %s>' % (self.name or self.id)

    @property
    def offset_from_playbook(self):
        return self.time_start - self.playbook.time_start

    @property
    def offset_from_play(self):
        return self.time_start - self.play.time_start


class Result(Base, TimedEntity):
    """
    The 'Result' class represents the result of running a single task on
    a single host.

    A 'Result' entity has the following relationships:
    - 'task' -- the task for which this is a result (via the 'results'
      relationship defined by 'Task').
    - 'host' -- the host associated with this result (via the 'results'
      relationship defined by 'Host')
    """
    __tablename__ = 'results'
    host_id = db.Column(db.Integer, db.ForeignKey('hosts.id'))
    play_id = db.Column(db.Integer, db.ForeignKey('plays.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))

    status = db.Column(db.Enum('ok', 'failed', 'skipped', 'unreachable'))
    changed = db.Column(db.Boolean, default=False)
    failed = db.Column(db.Boolean, default=False)
    skipped = db.Column(db.Boolean, default=False)
    unreachable = db.Column(db.Boolean, default=False)
    ignore_errors = db.Column(db.Boolean, default=False)
    result = db.Column(CompressedText((2**32) - 1))

    time_start = db.Column(db.DateTime, default=datetime.utcnow)
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
        return '<Result %s>' % self.host.name


class Host(Base):
    """
    The 'Host' object represents a host reference by an Ansible inventory.

    A 'Host' entity has the following relationships:
    - 'results' -- a list of 'Result' objects associated with this
      host.
    - 'stats' -- a list of 'Stats' objects resulting from playbook runs
      against this host.
    """
    __tablename__ = 'hosts'
    __table_args__ = (
        db.UniqueConstraint('playbook_id', 'name'),
    )
    facts = one_to_one('HostFacts', backref='host')
    results = one_to_many('Result', backref='host')
    stats = one_to_one('Stats', backref='host')

    name = db.Column(db.String(255), index=True)

    def __repr__(self):
        return '<Host %s>' % self.name


class HostFacts(Base):
    """
    The 'HostFacts' object represents a host reference by an Ansible
    inventory. It is meant to record facts when a setup task is run for a host.

    A 'HostFacts' entity has the following relationship:
    - 'hosts' -- the host owner of the facts
    """
    __tablename__ = 'host_facts'

    host_id = db.Column(db.Integer, db.ForeignKey('hosts.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    values = db.Column(CompressedData((2 ** 32) - 1))

    def __repr__(self):
        return '<HostFacts %s>' % self.host.name


class Stats(Base):
    """
    A 'Stats' object contains statistics for a single host from a single
    Ansible playbook run.

    A 'Stats' entity has the following relationships:
    - 'playbook' -- the playbook associated with these statistics (via the
      'stats' relationship defined in `Playbook`)
    - 'host' -- The host associated with these statistics (via the
      'stats' relationship defined in 'Host')
    """
    __tablename__ = 'stats'
    host_id = db.Column(db.Integer, db.ForeignKey('hosts.id'))

    changed = db.Column(db.Integer, default=0)
    failed = db.Column(db.Integer, default=0)
    ok = db.Column(db.Integer, default=0)
    skipped = db.Column(db.Integer, default=0)
    unreachable = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<Stats for %s>' % self.host.name


class Record(Base):
    """
    The 'Record' object represents a recorded key/value pair provided by the
    ara_record module.

    A 'Record' entity has the following relationships:
    - 'playbook' -- the playbook this key/value pair was recorded in
    """
    __tablename__ = 'records'
    __table_args__ = (
        db.UniqueConstraint('playbook_id', 'key'),
    )

    key = db.Column(db.String(255))
    value = db.Column(CompressedData((2 ** 32) - 1))
    type = db.Column(db.String(255))

    def __repr__(self):
        return '<Data %s:%s>' % (self.playbook_id, self.key)
