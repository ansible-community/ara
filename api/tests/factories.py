import factory

from api import models


class FileContentFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.FileContent
        django_get_or_create = ('sha1',)

    sha1 = '1e58ead094c920fad631d2c22df34dc0314dab0c'
    contents = b'x\x9cSV(\xc8I\xacL\xca\xcf\xcf\x06\x00\x11\xbd\x03\xa5'


class FileFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.File

    path = '/tmp/playbook.yml'
    content = factory.SubFactory(FileContentFactory)


class PlaybookFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Playbook

    ansible_version = '2.4.0'
    completed = True
    parameters = b'x\x9c\xabVJ\xcb\xcfW\xb2RPJJ,R\xaa\x05\x00 \x98\x04T'
    file = factory.SubFactory(FileFactory)
