# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging

import factory

try:
    from factory import DjangoModelFactory
except ImportError:
    # >3.0 moved the location of DjangoModelFactory
    from factory.django import DjangoModelFactory

from ara.api import models
from ara.api.tests import utils
from ara.setup import ara_version as ARA_VERSION

logging.getLogger("factory").setLevel(logging.INFO)

# constants for things like compressed byte strings or objects
FILE_CONTENTS = "---\n# Example file"
HOST_FACTS = {"ansible_fqdn": "hostname", "ansible_distribution": "CentOS"}
PLAYBOOK_ARGUMENTS = {"ansible_version": "2.5.5", "inventory": "/etc/ansible/hosts"}
RESULT_CONTENTS = {"results": [{"msg": "something happened"}]}
TASK_TAGS = ["always", "never"]
RECORD_LIST = ["one", "two", "three"]


class PlaybookFactory(DjangoModelFactory):
    class Meta:
        model = models.Playbook

    controller = "localhost"
    name = "test-playbook"
    user = "ara-user"
    ansible_version = "2.4.0"
    client_version = "0.16.7"
    server_version = ARA_VERSION
    python_version = "3.2.1"
    status = "running"
    arguments = utils.compressed_obj(PLAYBOOK_ARGUMENTS)
    path = "/path/playbook.yml"


class FileContentFactory(DjangoModelFactory):
    class Meta:
        model = models.FileContent
        django_get_or_create = ("sha1",)

    sha1 = utils.sha1(FILE_CONTENTS)
    contents = utils.compressed_str(FILE_CONTENTS)


class FileFactory(DjangoModelFactory):
    class Meta:
        model = models.File

    path = "/path/playbook.yml"
    content = factory.SubFactory(FileContentFactory)
    playbook = factory.SubFactory(PlaybookFactory)


class LabelFactory(DjangoModelFactory):
    class Meta:
        model = models.Label

    name = "test label"


class PlayFactory(DjangoModelFactory):
    class Meta:
        model = models.Play

    name = "test play"
    status = "running"
    uuid = "5c5f67b9-e63c-6297-80da-000000000005"
    playbook = factory.SubFactory(PlaybookFactory)


class TaskFactory(DjangoModelFactory):
    class Meta:
        model = models.Task

    name = "test task"
    uuid = "5c5f67b9-e63c-6297-80da-000000000006"
    status = "running"
    action = "setup"
    lineno = 2
    handler = False
    tags = utils.compressed_obj(TASK_TAGS)
    play = factory.SubFactory(PlayFactory)
    file = factory.SubFactory(FileFactory)
    playbook = factory.SubFactory(PlaybookFactory)


class HostFactory(DjangoModelFactory):
    class Meta:
        model = models.Host

    facts = utils.compressed_obj(HOST_FACTS)
    name = "hostname"
    playbook = factory.SubFactory(PlaybookFactory)
    changed = 0
    failed = 0
    ok = 0
    skipped = 0
    unreachable = 0


class LatestHostFactory(DjangoModelFactory):
    class Meta:
        model = models.LatestHost

    name = "hostname"
    host = factory.SubFactory(HostFactory, name=name)


class ResultFactory(DjangoModelFactory):
    class Meta:
        model = models.Result

    content = utils.compressed_obj(RESULT_CONTENTS)
    status = "ok"
    host = factory.SubFactory(HostFactory)
    # delegated_to expects a HostFactory to be assigned but it can also be []
    # when no delegation is done.
    # Though [] can't be declared here:
    #     TypeError: Direct assignment to the forward side of a many-to-many set is prohibited.
    # delegated_to = []
    task = factory.SubFactory(TaskFactory)
    play = factory.SubFactory(PlayFactory)
    playbook = factory.SubFactory(PlaybookFactory)
    changed = False
    ignore_errors = False


class RecordFactory(DjangoModelFactory):
    class Meta:
        model = models.Record

    key = "record-key"
    value = utils.compressed_obj(RECORD_LIST)
    type = "list"
    playbook = factory.SubFactory(PlaybookFactory)
