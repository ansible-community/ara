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

from ara import db


class Playbooks(db.Model):
    id = db.Column(db.String, primary_key=True, nullable=False)
    playbook = db.Column(db.String)
    start = db.Column(db.String)
    end = db.Column(db.String)
    duration = db.Column(db.String)
    tasks = db.relationship('Tasks', backref='playbooks', lazy='dynamic')
    stats = db.relationship('Stats', backref='playbooks', lazy='dynamic')

    def __repr__(self):
        return '<Playbook %r>' % self.playbook


class Tasks(db.Model):
    id = db.Column(db.String, primary_key=True, nullable=False)
    playbook_uuid = db.Column(db.String, db.ForeignKey('playbooks.id'))
    host = db.Column(db.String)
    play = db.Column(db.String)
    task = db.Column(db.String)
    module = db.Column(db.String)
    start = db.Column(db.String)
    end = db.Column(db.String)
    duration = db.Column(db.String)
    result = db.Column(db.Text)
    changed = db.Column(db.Integer)
    failed = db.Column(db.Integer)
    skipped = db.Column(db.Integer)
    unreachable = db.Column(db.Integer)
    ignore_errors = db.Column(db.Integer)

    def __repr__(self):
        return '<Task %r>' % self.task


class Stats(db.Model):
    id = db.Column(db.String, primary_key=True, nullable=False)
    playbook_uuid = db.Column(db.String, db.ForeignKey('playbooks.id'))
    host = db.Column(db.String)
    changed = db.Column(db.Integer)
    failures = db.Column(db.Integer)
    ok = db.Column(db.Integer)
    skipped = db.Column(db.Integer)
    unreachable = db.Column(db.Integer)

    def __repr__(self):
        return '<Stats %r>' % self.host
