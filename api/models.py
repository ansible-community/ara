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

import logging
from django.db import models
from django.utils import timezone

logger = logging.getLogger('ara_backend.models')


class Base(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)

    @property
    def age(self):
        """
        Calculates duration between created and updated.
        """
        return self.updated - self.created

    class Meta:
        abstract = True


class DurationMixin(models.Model):
    started = models.DateTimeField(default=timezone.now)
    ended = models.DateTimeField(blank=True, null=True)

    @property
    def duration(self):
        """
        Calculates duration between started and ended or between started and
        updated if we do not yet have an end.
        """
        if self.ended is None:
            if self.started is None:
                return timezone.timedelta(seconds=0)
            else:
                return self.updated - self.started
        return self.ended - self.started

    class Meta:
        abstract = True


class Playbook(Base, DurationMixin):
    """
    The 'playbook' table represents a single execution of the ansible or
    ansible-playbook commands. All the data for that execution is tied back
    to this one playbook.
    """
    class Meta:
        db_table = 'playbooks'

    path = models.CharField(max_length=255)
    ansible_version = models.CharField(max_length=255)
    parameters = models.BinaryField(max_length=(2 ** 32) - 1)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return '<Playbook %s:%s>' % (self.id, self.path)
    __repr__ = __str__


class FileContent(Base):
    class Meta:
        db_table = 'file_contents'

    sha1 = models.CharField(max_length=40, unique=True)
    contents = models.BinaryField(max_length=(2 ** 32) - 1)

    def __str__(self):
        return '<FileContent %s:%s>' % (self.id, self.sha1)
    __repr__ = __str__


class File(Base):
    class Meta:
        db_table = 'files'
        unique_together = ('path', 'playbook',)

    path = models.CharField(max_length=255)
    is_playbook = models.BooleanField(default=False)
    content = models.ForeignKey(FileContent,
                                on_delete=models.CASCADE,
                                related_name='files')
    playbook = models.ForeignKey(Playbook,
                                 on_delete=models.CASCADE,
                                 related_name='files')

    def __str__(self):
        return '<File %s:%s>' % (self.id, self.path)
    __repr__ = __str__


class Record(Base):
    class Meta:
        db_table = 'records'
        unique_together = ('key', 'playbook',)

    key = models.CharField(max_length=255)
    value = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=255)
    playbook = models.ForeignKey(Playbook,
                                 on_delete=models.CASCADE,
                                 related_name='records')

    def __str__(self):
        return '<Record %s:%s>' % (self.id, self.key)
    __repr__ = __str__


class Host(Base):
    class Meta:
        db_table = 'hosts'
        unique_together = ('name', 'playbook',)

    name = models.CharField(max_length=255)
    facts = models.BinaryField(max_length=(2 ** 32) - 1)
    changed = models.IntegerField(default=0)
    failed = models.IntegerField(default=0)
    ok = models.IntegerField(default=0)
    skipped = models.IntegerField(default=0)
    unreachable = models.IntegerField(default=0)
    playbook = models.ForeignKey(Playbook,
                                 on_delete=models.CASCADE,
                                 related_name='hosts')

    def __str__(self):
        return '<Host %s:%s>' % (self.id, self.name)
    __repr__ = __str__


class Play(Base, DurationMixin):
    class Meta:
        db_table = 'plays'

    name = models.TextField()
    playbook = models.ForeignKey(Playbook,
                                 on_delete=models.CASCADE,
                                 related_name='plays')

    @property
    def offset_from_playbook(self):
        return self.started - self.playbook.started

    def __str__(self):
        return '<Play %s:%s>' % (self.name, self.id)
    __repr__ = __str__


class Task(Base, DurationMixin):
    class Meta:
        db_table = 'tasks'

    name = models.TextField()
    action = models.TextField()
    lineno = models.IntegerField()
    tags = models.BinaryField(max_length=(2 ** 32) - 1)
    handler = models.BooleanField()

    playbook = models.ForeignKey(Playbook,
                                 on_delete=models.CASCADE,
                                 related_name='tasks')
    file = models.ForeignKey(File,
                             on_delete=models.DO_NOTHING,
                             related_name='tasks')
    play = models.ForeignKey(Play,
                             on_delete=models.DO_NOTHING,
                             related_name='tasks')

    @property
    def offset_from_playbook(self):
        return self.started - self.playbook.started

    @property
    def offset_from_play(self):
        return self.started - self.play.started

    def __str__(self):
        return '<Task %s:%s>' % (self.name, self.id)
    __repr__ = __str__


class Result(Base, DurationMixin):
    class Meta:
        db_table = 'results'

    # Ansible statuses
    OK = 'ok'
    FAILED = 'failed'
    SKIPPED = 'skipped'
    UNREACHABLE = 'unreachable'
    # ARA specific statuses (derived or assumed)
    CHANGED = 'changed'
    IGNORED = 'ignored'
    UNKNOWN = 'unknown'

    RESULT_STATUS = (
        (OK, 'ok'),
        (FAILED, 'failed'),
        (SKIPPED, 'skipped'),
        (UNREACHABLE, 'unreachable'),
        (UNKNOWN, 'unknown')
    )

    status = models.CharField(max_length=25,
                              choices=RESULT_STATUS,
                              default=UNKNOWN)
    changed = models.BooleanField(default=False)
    failed = models.BooleanField(default=False)
    skipped = models.BooleanField(default=False)
    unreachable = models.BooleanField(default=False)
    ignore_errors = models.BooleanField(default=False)
    result = models.BinaryField(max_length=(2 ** 32) - 1)
    playbook = models.ForeignKey(Playbook,
                                 on_delete=models.CASCADE,
                                 related_name='results')

    @property
    def derived_status(self):
        if self.status == self.OK and self.changed:
            return self.CHANGED
        elif self.status == self.FAILED and self.ignore_errors:
            return self.IGNORED
        elif self.status not in [
            self.OK, self.FAILED, self.SKIPPED, self.UNREACHABLE
        ]:
            return self.UNKNOWN
        else:
            return self.status

    def __str__(self):
        return '<Result %s:%s>' % (self.id, self.derived_status)
    __repr__ = __str__
