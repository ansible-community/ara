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

from datetime import datetime
import uuid
from ara import db

# This makes all the exceptions available as "models.<exception_name>".
from sqlalchemy.orm.exc import *  # NOQA


def mkuuid():
    return str(uuid.uuid4())


class TimedEntity(object):
    @property
    def duration(self):
        return self.time_end - self.time_start

    def start(self):
        self.time_start = datetime.now()

    def stop(self):
        self.time_end = datetime.now()


class Playbook(db.Model, TimedEntity):
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
        return '<Playbook %r>' % self.path


class Play(db.Model, TimedEntity):
    __tablename__ = 'plays'

    id = db.Column(db.String(36), primary_key=True, nullable=False,
                   default=mkuuid)
    playbook_id = db.Column(db.String(36), db.ForeignKey('playbooks.id'))
    name = db.Column(db.Text)
    tasks = db.relationship('Task', backref='play', lazy='dynamic')

    time_start = db.Column(db.DateTime, default=datetime.now)
    time_end = db.Column(db.DateTime)


class Task(db.Model, TimedEntity):
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
        return '<Task %r>' % self.name


class TaskResult(db.Model, TimedEntity):
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
        return '<TaskResult %r>' % self.host


class Host(db.Model):
    __tablename__ = 'hosts'

    id = db.Column(db.String(36), primary_key=True, nullable=False,
                   default=mkuuid)
    name = db.Column(db.Text)

    task_results = db.relationship('TaskResult', backref='host',
                                   lazy='dynamic')
    stats = db.relationship('Stats', backref='host',
                                   lazy='dynamic')


class Stats(db.Model):
    __tablename__ = 'stats'

    id = db.Column(db.String(36), primary_key=True, nullable=False,
                   default=mkuuid)
    playbook_id = db.Column(db.String(36), db.ForeignKey('playbooks.id'))
    host_id = db.Column(db.String(36), db.ForeignKey('hosts.id'))

    changed = db.Column(db.Integer)
    failures = db.Column(db.Integer)
    ok = db.Column(db.Integer)
    skipped = db.Column(db.Integer)
    unreachable = db.Column(db.Integer)

    def __repr__(self):
        return '<Stats %r>' % self.host
