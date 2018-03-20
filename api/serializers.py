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

import json
import hashlib
import logging
import zlib
from api import models
from django.utils import timezone
from rest_framework import serializers

DATE_FORMAT = "(iso-8601: 2016-05-06T17:20:25.749489-04:00)"
DURATION_FORMAT = "([DD] [HH:[MM:]]ss[.uuuuuu])"
logger = logging.getLogger('api.serializers')


class CompressedTextField(serializers.CharField):
    """
    Compresses text before storing it in the database.
    Decompresses text from the database before serving it.
    """

    def to_representation(self, obj):
        return zlib.decompress(obj).decode('utf8')

    def to_internal_value(self, data):
        return zlib.compress(data.encode('utf8'))


class CompressedObjectField(serializers.JSONField):
    """
    Serializes/compresses an object (i.e, list, dict) before storing it in the
    database.
    Decompresses/deserializes an object before serving it.
    """

    def to_representation(self, obj):
        return json.loads(zlib.decompress(obj).decode('utf8'))

    def to_internal_value(self, data):
        return zlib.compress(json.dumps(data).encode('utf8'))


class DurationSerializer(serializers.ModelSerializer):
    """
    Serializer for duration-based fields
    """

    class Meta:
        abstract = True

    duration = serializers.SerializerMethodField()

    @staticmethod
    def get_duration(obj):
        if obj.ended is None:
            return timezone.now() - obj.started
        return obj.ended - obj.started


class FileContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FileContent
        fields = '__all__'


class FileContentField(serializers.CharField):
    """
    Compresses text before storing it in the database.
    Decompresses text from the database before serving it.
    """

    def to_representation(self, obj):
        return zlib.decompress(obj.contents).decode('utf8')

    def to_internal_value(self, data):
        contents = zlib.compress(data.encode('utf8'))
        sha1 = hashlib.sha1(contents).hexdigest()
        content_file, created = models.FileContent.objects.get_or_create(sha1=sha1, defaults={
            'sha1': sha1,
            'contents': contents
        })
        return content_file


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.File
        fields = '__all__'

    content = FileContentField()


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Result
        fields = '__all__'


class PlaybookSerializer(DurationSerializer):
    class Meta:
        model = models.Playbook
        fields = '__all__'

    parameters = CompressedObjectField(
        default=zlib.compress(json.dumps({}).encode('utf8')),
        help_text='A JSON dictionary containing Ansible command parameters'
    )
    files = FileSerializer(many=True, default=[])
    results = ResultSerializer(read_only=True, many=True)

    def create(self, validated_data):
        files = validated_data.pop('files')
        playbook = models.Playbook.objects.create(**validated_data)
        for file in files:
            playbook.files.add(models.File.objects.create(**file))
        return playbook

    def update(self, instance, validated_data):
        files = validated_data.pop('files')
        return super(PlaybookSerializer, self).update(instance, validated_data)


class PlaySerializer(DurationSerializer):
    class Meta:
        model = models.Play
        fields = '__all__'

    results = ResultSerializer(read_only=True, many=True)


class TaskSerializer(DurationSerializer):
    class Meta:
        model = models.Task
        fields = '__all__'

    tags = CompressedObjectField(
        default=zlib.compress(json.dumps([]).encode('utf8')),
        help_text='A JSON list containing Ansible tags'
    )
