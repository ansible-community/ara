# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from rest_framework import serializers

from ara.api import fields as ara_fields, models


class ResultStatusSerializer(serializers.ModelSerializer):
    class Meta:
        abstract = True

    status = serializers.SerializerMethodField()

    @staticmethod
    def get_status(obj):
        if obj.status == "ok" and obj.changed:
            return "changed"
        elif obj.status == "failed" and obj.ignore_errors:
            return "ignored"
        else:
            return obj.status


class TaskPathSerializer(serializers.ModelSerializer):
    class Meta:
        abstract = True

    path = serializers.SerializerMethodField()

    @staticmethod
    def get_path(obj):
        return obj.file.path


class ItemCountSerializer(serializers.ModelSerializer):
    class Meta:
        abstract = True

    # For counting relationships to other objects
    items = serializers.SerializerMethodField()

    @staticmethod
    def get_items(obj):
        types = ["plays", "tasks", "results", "hosts", "files", "records"]
        items = {item: getattr(obj, item).count() for item in types if hasattr(obj, item)}
        return items


class FileSha1Serializer(serializers.ModelSerializer):
    class Meta:
        abstract = True

    # For retrieving the sha1 of a file's contents
    sha1 = serializers.SerializerMethodField()

    @staticmethod
    def get_sha1(obj):
        return obj.content.sha1


#######
# Simple serializers provide lightweight representations of objects suitable for inclusion in other objects
#######


class SimpleLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Label
        exclude = ("created", "updated")


class SimplePlaybookSerializer(ItemCountSerializer):
    class Meta:
        model = models.Playbook
        exclude = ("created", "updated")

    arguments = ara_fields.CompressedObjectField(default=ara_fields.EMPTY_DICT, read_only=True)
    labels = SimpleLabelSerializer(many=True, read_only=True, default=[])


class SimplePlaySerializer(ItemCountSerializer):
    class Meta:
        model = models.Play
        exclude = ("playbook", "uuid", "created", "updated")


class SimpleTaskSerializer(ItemCountSerializer, TaskPathSerializer):
    class Meta:
        model = models.Task
        exclude = ("playbook", "play", "created", "updated")

    tags = ara_fields.CompressedObjectField(read_only=True)


class SimpleHostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Host
        exclude = ("playbook", "facts", "created", "updated")


class SimpleFileSerializer(FileSha1Serializer):
    class Meta:
        model = models.File
        exclude = ("playbook", "content", "created", "updated")


#######
# Detailed serializers returns every field of an object as well as a simple
# representation of relationships to other objects.
#######


class DetailedLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Label
        fields = "__all__"


class DetailedPlaybookSerializer(ItemCountSerializer):
    class Meta:
        model = models.Playbook
        fields = "__all__"

    arguments = ara_fields.CompressedObjectField(default=ara_fields.EMPTY_DICT, read_only=True)
    labels = SimpleLabelSerializer(many=True, read_only=True, default=[])


class DetailedPlaySerializer(ItemCountSerializer):
    class Meta:
        model = models.Play
        fields = "__all__"

    playbook = SimplePlaybookSerializer(read_only=True)


class DetailedTaskSerializer(ItemCountSerializer, TaskPathSerializer):
    class Meta:
        model = models.Task
        fields = "__all__"

    playbook = SimplePlaybookSerializer(read_only=True)
    play = SimplePlaySerializer(read_only=True)
    file = SimpleFileSerializer(read_only=True)
    tags = ara_fields.CompressedObjectField(read_only=True)


class DetailedHostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Host
        fields = "__all__"

    playbook = SimplePlaybookSerializer(read_only=True)
    facts = ara_fields.CompressedObjectField(read_only=True)


class DetailedLatestHostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LatestHost
        fields = "__all__"

    host = DetailedHostSerializer(read_only=True)


class DetailedResultSerializer(ResultStatusSerializer):
    class Meta:
        model = models.Result
        fields = "__all__"

    playbook = SimplePlaybookSerializer(read_only=True)
    play = SimplePlaySerializer(read_only=True)
    task = SimpleTaskSerializer(read_only=True)
    host = SimpleHostSerializer(read_only=True)
    delegated_to = SimpleHostSerializer(many=True, read_only=True)
    content = ara_fields.CompressedObjectField(read_only=True)


class DetailedFileSerializer(FileSha1Serializer):
    class Meta:
        model = models.File
        fields = "__all__"

    playbook = SimplePlaybookSerializer(read_only=True)
    content = ara_fields.FileContentField(read_only=True)


class DetailedRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Record
        fields = "__all__"

    playbook = SimplePlaybookSerializer(read_only=True)
    value = ara_fields.CompressedObjectField(read_only=True)


#######
# List serializers returns lightweight fields about objects.
# Relationships are represented by numerical IDs.
#######


class ListLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Label
        fields = "__all__"


class ListPlaybookSerializer(ItemCountSerializer):
    class Meta:
        model = models.Playbook
        fields = "__all__"

    arguments = ara_fields.CompressedObjectField(default=ara_fields.EMPTY_DICT, read_only=True)
    labels = SimpleLabelSerializer(many=True, read_only=True, default=[])


class ListPlaySerializer(ItemCountSerializer):
    class Meta:
        model = models.Play
        fields = "__all__"

    playbook = serializers.PrimaryKeyRelatedField(read_only=True)


class ListTaskSerializer(ItemCountSerializer, TaskPathSerializer):
    class Meta:
        model = models.Task
        fields = "__all__"

    tags = ara_fields.CompressedObjectField(read_only=True)
    play = serializers.PrimaryKeyRelatedField(read_only=True)


class ListHostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Host
        exclude = ("facts",)

    playbook = serializers.PrimaryKeyRelatedField(read_only=True)


class ListResultSerializer(ResultStatusSerializer):
    class Meta:
        model = models.Result
        exclude = ("content",)

    playbook = serializers.PrimaryKeyRelatedField(read_only=True)
    play = serializers.PrimaryKeyRelatedField(read_only=True)
    task = serializers.PrimaryKeyRelatedField(read_only=True)
    host = serializers.PrimaryKeyRelatedField(read_only=True)
    delegated_to = serializers.PrimaryKeyRelatedField(many=True, read_only=True)


class ListFileSerializer(FileSha1Serializer):
    class Meta:
        model = models.File
        exclude = ("content",)

    playbook = serializers.PrimaryKeyRelatedField(read_only=True)


class ListRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Record
        exclude = ("value",)

    playbook = serializers.PrimaryKeyRelatedField(read_only=True)


#######
# Default serializers represents objects as they are modelized in the database.
# They are used for creating/updating/destroying objects.
#######


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Label
        fields = "__all__"


class PlaybookSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Playbook
        fields = "__all__"

    arguments = ara_fields.CompressedObjectField(default=ara_fields.EMPTY_DICT)
    labels = ara_fields.CreatableSlugRelatedField(
        many=True, slug_field="name", queryset=models.Label.objects.all(), required=False
    )


class PlaySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Play
        fields = "__all__"


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Task
        fields = "__all__"

    tags = ara_fields.CompressedObjectField(default=ara_fields.EMPTY_LIST, help_text="A list containing Ansible tags")


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
        models.LatestHost.objects.update_or_create(name=validated_data["name"], defaults={"host": host})
        return host


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Result
        fields = "__all__"

    content = ara_fields.CompressedObjectField(default=ara_fields.EMPTY_DICT)
    delegated_to = serializers.SlugRelatedField(
        many=True, required=False, slug_field="id", queryset=models.Host.objects.all()
    )


class FileSerializer(FileSha1Serializer):
    class Meta:
        model = models.File
        fields = "__all__"

    content = ara_fields.FileContentField()

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


class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Record
        fields = "__all__"

    value = ara_fields.CompressedObjectField(
        default=ara_fields.EMPTY_STRING, help_text="A string, list, dict, json or other formatted data"
    )
