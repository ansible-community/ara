# -*- coding: utf-8 -*-
import hashlib
import json
import logging
import zlib
from api import models
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

DATE_FORMAT = "(iso-8601: 2016-05-06T17:20:25.749489-04:00)"
DURATION_FORMAT = "([DD] [HH:[MM:]]ss[.uuuuuu])"
logger = logging.getLogger('api.serializers')


class CompressedTextField(serializers.CharField):
    def to_representation(self, obj):
        return zlib.decompress(obj).decode('utf8')

    def to_internal_value(self, data):
        return zlib.compress(data.encode('utf8'))


class CompressedObjectField(serializers.JSONField):
    def to_representation(self, obj):
        return json.loads(zlib.decompress(obj).decode('utf8'))

    def to_internal_value(self, data):
        return zlib.compress(data.encode('utf8'))


class SHA1Field(serializers.CharField):
    def to_representation(self, obj):
        return json.loads(lzma.decompress(obj).decode('utf8'))

    def to_internal_value(self, data):
        return lzma.compress(data.encode('utf8'))


class BaseSerializer(serializers.ModelSerializer):
    """
    Serializer for the data in the model base
    """
    created = serializers.DateTimeField(
        read_only=True, help_text='Date of creation %s' % DATE_FORMAT
    )
    updated = serializers.DateTimeField(
        read_only=True, help_text='Date of last update %s' % DATE_FORMAT
    )
    age = serializers.DurationField(
        read_only=True,
        help_text='Duration since the creation %s' % DURATION_FORMAT
    )

    class Meta:
        abstract = True


class DurationSerializer(serializers.ModelSerializer):
    """
    Serializer for duration-based fields
    """
    started = serializers.DateTimeField(
        initial=timezone.now().isoformat(),
        help_text='Date this item started %s' % DATE_FORMAT
    )
    ended = serializers.DateTimeField(
        required=False,
        help_text='Date this item ended %s' % DATE_FORMAT
    )
    duration = serializers.DurationField(
        read_only=True,
        help_text="Duration between 'started' and 'ended' %s" % DURATION_FORMAT
    )

    def validate(self, data):
        """
        Check that the start is before the end.
        """
        if 'ended' in data and (data['started'] > data['ended']):
            raise serializers.ValidationError(
                "'Ended' must be before 'started'"
            )
        return data

    class Meta:
        abstract = True


class PlaybookSerializer(BaseSerializer, DurationSerializer):
    class Meta:
        model = models.Playbook
        fields = '__all__'

    plays = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='plays',
        help_text='Plays associated to this playbook'
    )
#    tasks = serializers.HyperlinkedRelatedField(
#        many=True,
#        read_only=True,
#        view_name='tasks',
#        help_text='Tasks associated to this playbook'
#    )
#    hosts = serializers.HyperlinkedRelatedField(
#        many=True,
#        read_only=True,
#        view_name='hosts',
#        help_text='Hosts associated to this playbook'
#    )
#    results = serializers.HyperlinkedRelatedField(
#        many=True,
#        read_only=True,
#        view_name='results',
#        help_text='Results associated to this playbook'
#    )
#    records = serializers.HyperlinkedRelatedField(
#        many=True,
#        read_only=True,
#        view_name='records',
#        help_text='Records associated to this playbook'
#    )
#    files = serializers.HyperlinkedRelatedField(
#        many=True,
#        read_only=True,
#        view_name='files',
#        help_text='Records associated to this playbook'
#    )

    parameters = CompressedObjectField(
        initial={},
        help_text='A JSON dictionary containing Ansible command parameters'
    )
    path = serializers.CharField(help_text='Path to the playbook file')
    ansible_version = serializers.CharField(
        help_text='Version of Ansible used to run this playbook'
    )
    completed = serializers.BooleanField(
        help_text='If the completion of the execution has been acknowledged'
    )


class PlaySerializer(BaseSerializer, DurationSerializer):
    class Meta:
        model = models.Play
        fields = '__all__'


class TaskSerializer(BaseSerializer, DurationSerializer):
    class Meta:
        model = models.Task
        fields = '__all__'


class HostSerializer(BaseSerializer):
    class Meta:
        model = models.Host
        fields = '__all__'


class ResultSerializer(BaseSerializer, DurationSerializer):
    class Meta:
        model = models.Result
        fields = '__all__'


class RecordSerializer(BaseSerializer):
    class Meta:
        model = models.Record
        fields = '__all__'


class FileContentSerializer(BaseSerializer):
    class Meta:
        model = models.FileContent
        fields = ('contents', 'sha1')

    contents = CompressedTextField(help_text='Contents of the file')
    sha1 = serializers.CharField(read_only=True, help_text='sha1 of the file')

    def create(self, validated_data):
        sha1 = hashlib.sha1(validated_data['contents']).hexdigest()
        validated_data['sha1'] = sha1
        obj, created = models.FileContent.objects.get_or_create(
            **validated_data
        )
        return obj


class FileSerializer(BaseSerializer):
    path = serializers.CharField(help_text='Path to the file')
    content = FileContentSerializer()

    def create(self, validated_data):
        contents = validated_data.pop('content')['contents']
        obj, created = models.FileContent.objects.get_or_create(
            contents=contents,
            sha1=hashlib.sha1(contents).hexdigest()
        )
        validated_data['content'] = obj
        return models.File.objects.create(**validated_data)

    class Meta:
        model = models.File
        fields = ('id', 'path', 'content', 'playbook')
