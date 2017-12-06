import factory

from api import models


class PlaybookFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Playbook

    path = '/tmp/playbook.yml'
    ansible_version = '2.4.0'
