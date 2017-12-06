import uuid
from django.db import models


class Base(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class DateMixin(Base):
    start = models.DateTimeField(auto_now_add=True, verbose_name='started')
    ended = models.DateTimeField(auto_now=True, verbose_name='ended')

    class Meta:
        abstract = True


class Playbook(DateMixin):
    path = models.CharField(max_length=255)
    ansible_version = models.CharField(max_length=255)
    parameters = models.TextField(null=True, blank=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return '<Playbook %s>' % self.id


class File(Base):
    content = models.FileField(upload_to='files/%Y/%m/%d/')
    is_playbook = models.BooleanField(default=False)
    playbook_id = models.ForeignKey(Playbook, on_delete=models.CASCADE, related_name='files')


class Record(DateMixin):
    key = models.CharField(max_length=255)
    value = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=255)
    playbook_id = models.ForeignKey(Playbook, on_delete=models.CASCADE, related_name='records')

    def __str__(self):
        return '<Record %s>' % self.id


class Host(DateMixin):
    name = models.CharField(max_length=255)
    facts = models.TextField(null=True, blank=True)
    changed = models.IntegerField(default=0)
    failed = models.IntegerField(default=0)
    ok = models.IntegerField(default=0)
    skipped = models.IntegerField(default=0)
    unreachable = models.IntegerField(default=0)
    playbook_id = models.ForeignKey(Playbook, on_delete=models.CASCADE, related_name='hosts')

    def __str__(self):
        return '<Host %s:%s>' % (self.name, self.id)


OK = "ok"
FAILED = "failed"
SKIPPED = "skipped"
UNREACHABLE = "unreachable"

RESULT_STATUS = (
    (OK, "ok"),
    (FAILED, "failed"),
    (SKIPPED, "skipped"),
    (UNREACHABLE, "unreachable")
)


class Play(DateMixin):
    name = models.TextField(null=True, blank=True)
    playbook_id = models.ForeignKey(Playbook, on_delete=models.CASCADE, related_name='plays')

    def __str__(self):
        return '<Play %s:%s>' % (self.name, self.id)


class Task(DateMixin):
    name = models.TextField(null=True, blank=True)
    action = models.TextField(null=True, blank=True)
    lineno = models.IntegerField()
    tags = models.TextField(null=True, blank=True)
    handler = models.BooleanField()
    playbook_id = models.ForeignKey(Playbook, on_delete=models.CASCADE, related_name='tasks')

    def __str__(self):
        return '<Task %s:%s>' % (self.name, self.id)


class Result(DateMixin):
    status = models.CharField(max_length=11, choices=RESULT_STATUS, null=True, blank=True)
    changed = models.BooleanField(default=False)
    failed = models.BooleanField(default=False)
    skipped = models.BooleanField(default=False)
    unreachable = models.BooleanField(default=False)
    ignore_errors = models.BooleanField(default=False)
    result = models.TextField(null=True, blank=True)
    playbook_id = models.ForeignKey(Playbook, on_delete=models.CASCADE, related_name='results')

    def __str__(self):
        return '<Result %s>' % self.id
