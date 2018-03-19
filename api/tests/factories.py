import factory

from api import models


class PlaybookFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Playbook

    path = '/tmp/playbook.yml'
    ansible_version = '2.4.0'
    parameters = b'x\x9c\xabVJ\xcb\xcfW\xb2RPJJ,R\xaa\x05\x00 \x98\x04T'


class FileContentFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.FileContent

    sha1 = '1e58ead094c920fad631d2c22df34dc0314dab0c'
    contents = b'x\x9cSV(\xc8I\xacL\xca\xcf\xcf\x06\x00\x11\xbd\x03\xa5'
