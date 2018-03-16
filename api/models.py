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

logger = logging.getLogger('ara_backend.models')

# TODO: Figure out what to do when creating the first playbook file
# -> create playbook first
# -> create file/file_content and link to playbook_id (foreign key)
# -> make is_playbook = True because it's a playbook file
# -> Add a unique constraint on "is_playbook = True" for a given playbook id ?

# TODO: Get feedback on model
# playbook -> play -> task -> host -> result
#                  -> host (hosts are associated/filtered to a play)
# playbook -> file <- file_content
# task -> file <- file_content
# statistics for a playbook are cumulated per host
# facts are retrieved for a host (printing those in CLI is terrible)

# - There's multiple results for a host throughout a playbook
# - There's multiple hosts for a task
# - There's multiple tasks in a play
# - There's multiple play in a playbook
# - Hosts need to be associated to a play
# - Should all the binary things be in a single table so it's easier to shard ?
# - e.g, Reddit's ThingDB


class Base(models.Model):
    """
    Abstract base model part of every model
    """
    class Meta:
        abstract = True

    id = models.BigAutoField(primary_key=True, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)


class DurationMixin(models.Model):
    """
    Abstract model for models with a concept of duration
    """
    class Meta:
        abstract = True

    started = models.DateTimeField(default=timezone.now)
    ended = models.DateTimeField(blank=True, null=True)


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


class FileContent(Base):
    """
    Contents of a uniquely stored and compressed file.
    Running the same playbook twice will yield two playbook files but just
    one file contents.
    """
    class Meta:
        db_table = 'file_contents'

    sha1 = models.CharField(max_length=40, unique=True)
    contents = models.BinaryField(max_length=(2 ** 32) - 1)

    def __str__(self):
        return '<FileContent %s:%s>' % (self.id, self.sha1)


class File(Base):
    """
    Data about Ansible files (playbooks, tasks, role files, var files, etc).
    Multiple files can reference the same FileContent record.
    """
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


class Record(Base):
    """
    A rudimentary key/value table to associate arbitrary data to a playbook.
    Used with the ara_record and ara_read Ansible modules.
    """
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


class Play(Base, DurationMixin):
    """
    Data about Ansible plays.
    Hosts, tasks and results are childrens of an Ansible play.
    """
    class Meta:
        db_table = 'plays'

    name = models.TextField(blank=True, null=True)
    playbook = models.ForeignKey(Playbook,
                                 on_delete=models.CASCADE,
                                 related_name='plays')

    def __str__(self):
        return '<Play %s:%s>' % (self.name, self.id)


class Host(Base):
    """
    Data about Ansible hosts.
    Contains compressed host facts and statistics about the host for the
    playbook.
    """
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
    play = models.ForeignKey(Play,
                             on_delete=models.DO_NOTHING,
                             related_name='hosts')

    def __str__(self):
        return '<Host %s:%s>' % (self.id, self.name)


class Task(Base, DurationMixin):
    """
    Data about Ansible tasks.
    Results are children of Ansible tasks.
    """
    class Meta:
        db_table = 'tasks'

    name = models.TextField(blank=True, null=True)
    action = models.TextField()
    lineno = models.IntegerField()
    tags = models.BinaryField(max_length=(2 ** 32) - 1)
    handler = models.BooleanField()

    playbook = models.ForeignKey(Playbook,
                                 on_delete=models.CASCADE,
                                 related_name='tasks')
    play = models.ForeignKey(Play,
                             on_delete=models.CASCADE,
                             related_name='tasks')
    file = models.ForeignKey(File,
                             on_delete=models.DO_NOTHING,
                             related_name='tasks')

    def __str__(self):
        return '<Task %s:%s>' % (self.name, self.id)


class Result(Base, DurationMixin):
    """
    Data about Ansible results.
    A task can have many results if the task is run on multiple hosts.
    """
    class Meta:
        db_table = 'results'

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
    play = models.ForeignKey(Play,
                             on_delete=models.CASCADE,
                             related_name='results')
    task = models.ForeignKey(Task,
                             on_delete=models.CASCADE,
                             related_name='results')
    host = models.ForeignKey(Host,
                             on_delete=models.CASCADE,
                             related_name='results')

    def __str__(self):
        return '<Result %s, %s:%s>' % (self.id, self.host.name, self.status)
