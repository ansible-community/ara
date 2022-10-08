# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django.db import models
from django.utils import timezone

from ara.setup import ara_version


class Base(models.Model):
    """
    Abstract base model part of every model
    """

    class Meta:
        abstract = True

    id = models.BigAutoField(primary_key=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Duration(Base):
    """
    Abstract model for models with a concept of duration
    """

    class Meta:
        abstract = True

    started = models.DateTimeField(default=timezone.now)
    ended = models.DateTimeField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Compute duration based on available timestamps
        if self.ended is not None:
            self.duration = self.ended - self.started
        return super().save(*args, **kwargs)


class Label(Base):
    """
    A label is a generic container meant to group or correlate different
    playbooks. It could be a single playbook run. It could be a "group" of
    playbooks.
    It could represent phases or dynamic logical grouping and tagging of
    playbook runs.
    You could have a label named "failures" and make it so failed playbooks
    are added to this report, for example.
    The main purpose of this is to make the labels customizable by the user.
    """

    class Meta:
        db_table = "labels"

    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return "<Label %s: %s>" % (self.id, self.name)


class Playbook(Duration):
    """
    An entry in the 'playbooks' table represents a single execution of the
    ansible or ansible-playbook commands. All the data for that execution
    is tied back to this one playbook.
    """

    class Meta:
        db_table = "playbooks"

    # A playbook in ARA can be running (in progress), completed (succeeded) or failed.
    UNKNOWN = "unknown"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    STATUS = (
        (UNKNOWN, "unknown"),
        (EXPIRED, "expired"),
        (RUNNING, "running"),
        (COMPLETED, "completed"),
        (FAILED, "failed"),
    )

    name = models.CharField(max_length=255, null=True)
    ansible_version = models.CharField(max_length=255)
    client_version = models.CharField(max_length=255, null=True)
    python_version = models.CharField(max_length=255, null=True)
    server_version = models.CharField(max_length=255, default=ara_version)
    status = models.CharField(max_length=25, choices=STATUS, default=UNKNOWN)
    arguments = models.BinaryField(max_length=(2**32) - 1)
    path = models.CharField(max_length=255)
    labels = models.ManyToManyField(Label)
    controller = models.CharField(max_length=255, null=True, default="localhost")
    user = models.CharField(max_length=255, null=True)

    def __str__(self):
        return "<Playbook %s>" % self.id


class FileContent(Base):
    """
    Contents of a uniquely stored and compressed file.
    Running the same playbook twice will yield two playbook files but just
    one file contents.
    """

    class Meta:
        db_table = "file_contents"

    sha1 = models.CharField(max_length=40, unique=True)
    contents = models.BinaryField(max_length=(2**32) - 1)

    def __str__(self):
        return "<FileContent %s:%s>" % (self.id, self.sha1)


class File(Base):
    """
    Data about Ansible files (playbooks, tasks, role files, var files, etc).
    Multiple files can reference the same FileContent record.
    """

    class Meta:
        db_table = "files"
        unique_together = ("path", "playbook")

    path = models.CharField(max_length=255)
    content = models.ForeignKey(FileContent, on_delete=models.CASCADE, related_name="files")
    playbook = models.ForeignKey(Playbook, on_delete=models.CASCADE, related_name="files")

    def __str__(self):
        return "<File %s:%s>" % (self.id, self.path)


class Record(Base):
    """
    A rudimentary key/value table to associate arbitrary data to a playbook.
    Used with the ara_record and ara_read Ansible modules.
    """

    class Meta:
        db_table = "records"
        unique_together = ("key", "playbook")

    key = models.CharField(max_length=255)
    value = models.BinaryField(max_length=(2**32) - 1)
    type = models.CharField(max_length=255)
    playbook = models.ForeignKey(Playbook, on_delete=models.CASCADE, related_name="records")

    def __str__(self):
        return "<Record %s:%s>" % (self.id, self.key)


class Play(Duration):
    """
    Data about Ansible plays.
    Hosts, tasks and results are childrens of an Ansible play.
    """

    class Meta:
        db_table = "plays"

    # A play in ARA can be running (in progress) or completed (regardless of success or failure)
    UNKNOWN = "unknown"
    RUNNING = "running"
    COMPLETED = "completed"
    EXPIRED = "expired"
    STATUS = ((UNKNOWN, "unknown"), (RUNNING, "running"), (COMPLETED, "completed"), (EXPIRED, "expired"))

    name = models.CharField(max_length=255, blank=True, null=True)
    uuid = models.UUIDField()
    status = models.CharField(max_length=25, choices=STATUS, default=UNKNOWN)
    playbook = models.ForeignKey(Playbook, on_delete=models.CASCADE, related_name="plays")

    def __str__(self):
        return "<Play %s:%s>" % (self.id, self.name)


class Task(Duration):
    """Data about Ansible tasks."""

    class Meta:
        db_table = "tasks"

    # Possible statuses for a task
    # A failed task is expected to have at least one failed result
    COMPLETED = "completed"
    EXPIRED = "expired"
    FAILED = "failed"
    RUNNING = "running"
    UNKNOWN = "unknown"

    STATUS = (
        (COMPLETED, "completed"),
        (EXPIRED, "expired"),
        (FAILED, "failed"),
        (RUNNING, "running"),
        (UNKNOWN, "unknown"),
    )

    name = models.TextField(blank=True, null=True)
    uuid = models.UUIDField(null=True)
    action = models.TextField()
    lineno = models.IntegerField()
    tags = models.BinaryField(max_length=(2**32) - 1)
    handler = models.BooleanField()
    status = models.CharField(max_length=25, choices=STATUS, default=UNKNOWN)

    play = models.ForeignKey(Play, on_delete=models.CASCADE, related_name="tasks")
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name="tasks")
    playbook = models.ForeignKey(Playbook, on_delete=models.CASCADE, related_name="tasks")

    def __str__(self):
        return "<Task %s:%s>" % (self.name, self.id)


class Host(Base):
    """
    Data about Ansible hosts.
    """

    class Meta:
        db_table = "hosts"
        unique_together = ("name", "playbook")

    name = models.CharField(max_length=255)
    facts = models.BinaryField(max_length=(2**32) - 1)

    changed = models.IntegerField(default=0)
    failed = models.IntegerField(default=0)
    ok = models.IntegerField(default=0)
    skipped = models.IntegerField(default=0)
    unreachable = models.IntegerField(default=0)

    playbook = models.ForeignKey(Playbook, on_delete=models.CASCADE, related_name="hosts")

    def __str__(self):
        return "<Host %s:%s>" % (self.id, self.name)


class LatestHost(models.Model):
    """
    Latest record of each host based on name, referring to `Host` object id related.

    We can not inherit from Base because we want to use `name` as primary key.
    """

    class Meta:
        db_table = "latest_hosts"

    name = models.CharField(max_length=255, primary_key=True)
    host = models.ForeignKey(Host, on_delete=models.CASCADE)

    # because we can't inherit from Base (see above) we have to define this here additionally
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "<LatestHost %s>" % (self.name)


class Result(Duration):
    """
    Data about Ansible results.
    A task can have many results if the task is run on multiple hosts.
    """

    class Meta:
        db_table = "results"

    # Ansible statuses
    OK = "ok"
    FAILED = "failed"
    SKIPPED = "skipped"
    UNREACHABLE = "unreachable"
    # ARA specific status, it's the default when not specified
    UNKNOWN = "unknown"

    # fmt:off
    STATUS = (
        (OK, "ok"),
        (FAILED, "failed"),
        (SKIPPED, "skipped"),
        (UNREACHABLE, "unreachable"),
        (UNKNOWN, "unknown"),
    )
    # fmt:on

    status = models.CharField(max_length=25, choices=STATUS, default=UNKNOWN)
    changed = models.BooleanField(default=False)
    ignore_errors = models.BooleanField(default=False)

    # todo use a single Content table
    content = models.BinaryField(max_length=(2**32) - 1)
    host = models.ForeignKey(Host, on_delete=models.CASCADE, related_name="results")
    delegated_to = models.ManyToManyField(Host)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="results")
    play = models.ForeignKey(Play, on_delete=models.CASCADE, related_name="results")
    playbook = models.ForeignKey(Playbook, on_delete=models.CASCADE, related_name="results")

    def __str__(self):
        return "<Result %s, %s>" % (self.id, self.status)
