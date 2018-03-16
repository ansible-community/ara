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
        return zlib.compress(data.encode('utf8'))


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

    started = serializers.DateTimeField(
        initial=timezone.now().isoformat(),
        help_text='Date this item started %s' % DATE_FORMAT
    )
    ended = serializers.DateTimeField(
        required=False,
        help_text='Date this item ended %s' % DATE_FORMAT
    )
    duration = ItemDurationField(source='*')

    def validate(self, data):
        """
        Check that the start is before the end.
        """
        if 'ended' in data and (data['started'] > data['ended']):
            raise serializers.ValidationError(
                "'Ended' must be before 'started'"
            )
        return data


class PlaybookSerializer(serializers.HyperlinkedModelSerializer, BaseSerializer, DurationSerializer):
    class Meta:
        model = models.Playbook
        fields = '__all__'

    plays = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='play-detail',
        read_only=True,
        help_text='Plays associated to this playbook'
    )
    tasks = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='task-detail',
        read_only=True,
        help_text='Tasks associated to this playbook'
    )

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
    files = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='file-detail',
        read_only=True,
        help_text='Files associated to this playbook'
    )
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


class PlaySerializer(serializers.HyperlinkedModelSerializer, BaseSerializer, DurationSerializer):
    class Meta:
        model = models.Play
        fields = '__all__'

        playbook = serializers.HyperlinkedRelatedField(
            view_name='playbook-detail',
            read_only=True,
            help_text='Playbook associated to this play'
        )
        tasks = serializers.HyperlinkedRelatedField(
            many=True,
            view_name='task-detail',
            read_only=True,
            help_text='Tasks associated to this play'
        )
        name = serializers.CharField(
            help_text='Name of the play',
            allow_blank=True,
            allow_null=True,
        )
        # hosts = serializers.HyperlinkedRelatedField(
        #    many=True,
        #    view_name='host-detail',
        #    read_only=True,
        #    help_text='Hosts associated to this play'
        #)


class TaskSerializer(serializers.HyperlinkedModelSerializer, BaseSerializer, DurationSerializer):
    class Meta:
        model = models.Task
        fields = '__all__'

        playbook = serializers.HyperlinkedRelatedField(
            view_name='playbook-detail',
            read_only=True,
            help_text='Playbook associated to this task'
        )
        play = serializers.HyperlinkedRelatedField(
            view_name='play-detail',
            read_only=True,
            help_text='Play associated to this task'
        )
        file = serializers.HyperlinkedRelatedField(
            view_name='file-detail',
            read_only=True,
            help_text='File associated to this task'
        )
        # results = serializers.HyperlinkedRelatedField(
        #     many=True,
        #     view_name='result-detail',
        #     read_only=True,
        #     help_text='Results associated to this task'
        # )
        name = serializers.CharField(
            help_text='Name of the task',
            allow_blank=True,
            allow_null=True
        )
        action = serializers.CharField(help_text='Action of the task')
        lineno = serializers.IntegerField(
            help_text='Line number in the file of the task'
        )
        tags = CompressedObjectField(
            help_text='A JSON list containing Ansible tags',
            initial=[],
            default=[],
        )
        handler = serializers.BooleanField(
            help_text='Whether or not this task was a handler',
            initial=False,
            default=False,
        )

#
#
# class HostSerializer(BaseSerializer):
#     class Meta:
#         model = models.Host
#         fields = '__all__'
#
#
# class ResultSerializer(BaseSerializer, DurationSerializer):
#     class Meta:
#         model = models.Result
#         fields = '__all__'
#     @property
#      def derived_status(self):
#          if self.status == self.OK and self.changed:
#              return self.CHANGED
#          elif self.status == self.FAILED and self.ignore_errors:
#              return self.IGNORED
#          elif self.status not in [
#              self.OK, self.FAILED, self.SKIPPED, self.UNREACHABLE
#          ]:
#              return self.UNKNOWN
#          else:
#              return self.status
#
# class RecordSerializer(BaseSerializer):
#     class Meta:
#         model = models.Record
#         fields = '__all__'
#


class FileContentSerializer(BaseSerializer):
    class Meta:
        model = models.FileContent
        fields = '__all__'

    contents = CompressedTextField(help_text='Contents of the file')
    sha1 = serializers.CharField(read_only=True, help_text='sha1 of the file')

    def create(self, validated_data):
        sha1 = hashlib.sha1(validated_data['contents']).hexdigest()
        validated_data['sha1'] = sha1
        obj, created = models.FileContent.objects.get_or_create(
            **validated_data
        )
        return obj


class FileSerializer(serializers.HyperlinkedModelSerializer, BaseSerializer):
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
