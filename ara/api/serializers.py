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

from rest_framework import serializers

from ara.api import fields as ara_fields, models


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
            return obj.updated - obj.started
        return obj.ended - obj.started


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.File
        fields = "__all__"

    sha1 = serializers.SerializerMethodField()
    content = ara_fields.FileContentField()

    @staticmethod
    def get_sha1(obj):
        return obj.content.sha1

    def get_unique_together_validators(self):
        """
        Files have a "unique together" constraint for file.path and playbook.id.
        We want to have a "get_or_create" facility and in order to do that, we
        must manage the validation during the creation, not before.
        Overriding this method effectively disables this validator.
        """
        return []

    def create(self, validated_data):
        file_, created = models.File.objects.get_or_create(
            path=validated_data["path"],
            content=validated_data["content"],
            playbook=validated_data["playbook"],
            defaults=validated_data,
        )
        return file_


class HostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Host
        fields = "__all__"

    facts = ara_fields.CompressedObjectField(default=ara_fields.EMPTY_DICT)

    def get_unique_together_validators(self):
        """
        Hosts have a "unique together" constraint for host.name and play.id.
        We want to have a "get_or_create" facility and in order to do that, we
        must manage the validation during the creation, not before.
        Overriding this method effectively disables this validator.
        """
        return []

    def create(self, validated_data):
        host, created = models.Host.objects.get_or_create(
            name=validated_data["name"], playbook=validated_data["playbook"], defaults=validated_data
        )
        return host


class ResultSerializer(DurationSerializer):
    class Meta:
        model = models.Result
        fields = "__all__"

    content = ara_fields.CompressedObjectField(default=ara_fields.EMPTY_DICT)


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Label
        fields = "__all__"

    description = ara_fields.CompressedTextField(
        default=ara_fields.EMPTY_STRING, help_text="A text description of the label"
    )


class TaskSerializer(DurationSerializer):
    class Meta:
        model = models.Task
        fields = "__all__"

    tags = ara_fields.CompressedObjectField(default=ara_fields.EMPTY_LIST, help_text="A list containing Ansible tags")


class SimpleTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Task
        fields = ("id", "name")


class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Record
        fields = "__all__"

    value = ara_fields.CompressedObjectField(
        default=ara_fields.EMPTY_STRING, help_text="A string, list, dict, json or other formatted data"
    )


class PlaySerializer(DurationSerializer):
    class Meta:
        model = models.Play
        fields = "__all__"

    hosts = HostSerializer(read_only=True, many=True)
    results = ResultSerializer(read_only=True, many=True)


class SimplePlaySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Play
        fields = "__all__"


class StatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Stats
        fields = "__all__"


class PlaybookSerializer(DurationSerializer):
    class Meta:
        model = models.Playbook
        fields = "__all__"

    arguments = ara_fields.CompressedObjectField(default=ara_fields.EMPTY_DICT)
    files = FileSerializer(many=True, read_only=True, default=[])
    hosts = HostSerializer(many=True, read_only=True, default=[])
    labels = LabelSerializer(many=True, read_only=True, default=[])
    tasks = SimpleTaskSerializer(many=True, read_only=True, default=[])
    plays = SimplePlaySerializer(many=True, read_only=True, default=[])
    records = RecordSerializer(many=True, read_only=True, default=[])
