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


class ItemDurationField(serializers.DurationField):
    """
    Calculates duration between started and ended or between started and
    updated if we do not yet have an end.
    """

    def __init__(self, **kwargs):
        kwargs['read_only'] = True
        super(ItemDurationField, self).__init__(**kwargs)

    def to_representation(self, obj):
        if obj.ended is None:
            if obj.started is None:
                return timezone.timedelta(seconds=0)
            else:
                return obj.updated - obj.started
        return obj.ended - obj.started


class BaseSerializer(serializers.ModelSerializer):
    """
    Serializer for the data in the model base
    """

    class Meta:
        abstract = True

    id = serializers.IntegerField(read_only=True)
    created = serializers.DateTimeField(
        read_only=True,
        help_text='Date of creation %s' % DATE_FORMAT
    )
    updated = serializers.DateTimeField(
        read_only=True,
        help_text='Date of last update %s' % DATE_FORMAT
    )


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


class PlaybookSerializer(DurationSerializer):
    class Meta:
        model = models.Playbook
        fields = '__all__'

    path = serializers.CharField(help_text='Path to the playbook file')
    ansible_version = serializers.CharField(
        help_text='Version of Ansible used to run this playbook'
    )
    parameters = CompressedObjectField(
        default=zlib.compress(json.dumps({}).encode('utf8')),
        help_text='A JSON dictionary containing Ansible command parameters'
    )
    completed = serializers.BooleanField(
        default=False,
        help_text='If the completion of the execution has been acknowledged'
    )
    plays = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    tasks = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    files = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    hosts = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    results = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    records = serializers.PrimaryKeyRelatedField(many=True, read_only=True)


class PlaySerializer(DurationSerializer):
    class Meta:
        model = models.Play
        fields = '__all__'


class TaskSerializer(DurationSerializer):
    class Meta:
        model = models.Task
        fields = '__all__'

    tags = CompressedObjectField(
        default=zlib.compress(json.dumps([]).encode('utf8')),
        help_text='A JSON list containing Ansible tags'
    )


class FileContentSerializer(BaseSerializer):
    class Meta:
        model = models.FileContent
        fields = '__all__'

    sha1 = serializers.CharField(read_only=True, help_text='sha1 of the file')
    contents = CompressedTextField(help_text='Contents of the file')

    def create(self, validated_data):
        sha1 = hashlib.sha1(validated_data['contents']).hexdigest()
        validated_data['sha1'] = sha1
        return models.FileContent.objects.create(**validated_data)


class FileSerializer(BaseSerializer):
    class Meta:
        model = models.File
        fields = '__all__'

    # TODO: Why doesn't this work ? There's no playbook field shown.
    # Works just fine in other serializers (ex: task)
    # playbook = serializers.HyperlinkedRelatedField(
    #     view_name='playbook-detail',
    #     read_only=True,
    #     help_text='Playbook associated to this file'
    # )
    path = serializers.CharField(help_text='Path to the file')
    # TODO: This probably needs to be a related field to filecontent serializer
    content = serializers.CharField()
    is_playbook = serializers.BooleanField(default=False)

    def create(self, validated_data):
        content = validated_data.pop('content')
        obj, created = models.FileContent.objects.get_or_create(
            contents=content.encode('utf8'),
            sha1=hashlib.sha1(content.encode('utf8')).hexdigest()
        )
        validated_data['content'] = obj
        return models.File.objects.create(**validated_data)
