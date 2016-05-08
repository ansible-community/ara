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
    id = db.Column('id', db.String, primary_key=True, nullable=False)
    playbook = db.Column('playbook', db.String)
    start = db.Column('start', db.String)
    end = db.Column('end', db.String)
    duration = db.Column('duration', db.String)

    def __repr__(self):
        return '<Playbook %r>' % self.playbook


class Tasks(db.Model):
    id = db.Column('id', db.Integer, primary_key=True, nullable=False,
                   autoincrement=True)
    playbook_uuid = db.Column('playbook_uuid', db.String)
    host = db.Column('host', db.String)
    play = db.Column('play', db.String)
    task = db.Column('task', db.String)
    start = db.Column('start', db.String)
    end = db.Column('end', db.String)
    duration = db.Column('duration', db.String)
    result = db.Column('result', db.Text)
    changed = db.Column('changed', db.Integer)
    skipped = db.Column('skipped', db.Integer)
    failed = db.Column('failed', db.Integer)

    def __repr__(self):
        return '<Task %r>' % self.task


class Stats(db.Model):
    id = db.Column('id', db.Integer, primary_key=True, nullable=False,
                   autoincrement=True)
    playbook_uuid = db.Column('playbook_uuid', db.String)
    host = db.Column('host', db.String)
    changed = db.Column('changed', db.Integer)
    failures = db.Column('failures', db.Integer)
    ok = db.Column('ok', db.Integer)
    skipped = db.Column('skipped', db.Integer)

    def __repr__(self):
        return '<Stats %r>' % self.host
