# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import collections
import hashlib
import json
import zlib

from rest_framework import serializers

from ara.api import models

# Constants used for defaults which rely on compression so we don't need to
# reproduce this code elsewhere.
EMPTY_DICT = zlib.compress(json.dumps({}).encode("utf8"))
EMPTY_LIST = zlib.compress(json.dumps([]).encode("utf8"))
EMPTY_STRING = zlib.compress(json.dumps("").encode("utf8"))


class CompressedTextField(serializers.CharField):
    """
    Compresses text before storing it in the database.
    Decompresses text from the database before serving it.
    """

    def to_representation(self, obj):
        return zlib.decompress(obj).decode("utf8")

    def to_internal_value(self, data):
        return zlib.compress(data.encode("utf8"))


class CompressedObjectField(serializers.JSONField):
    """
    Serializes/compresses an object (i.e, list, dict) before storing it in the
    database.
    Decompresses/deserializes an object before serving it.
    """

    def to_representation(self, obj):
        return json.loads(zlib.decompress(obj).decode("utf8"))

    def to_internal_value(self, data):
        return zlib.compress(json.dumps(data).encode("utf8"))


class FileContentField(serializers.CharField):
    """
    Compresses text before storing it in the database.
    Decompresses text from the database before serving it.
    """

    def to_representation(self, obj):
        return zlib.decompress(obj.contents).decode("utf8")

    def to_internal_value(self, data):
        contents = data.encode("utf8")
        sha1 = hashlib.sha1(contents).hexdigest()
        content_file, created = models.FileContent.objects.get_or_create(
            sha1=sha1, defaults={"sha1": sha1, "contents": zlib.compress(contents)}
        )
        return content_file


class CreatableSlugRelatedField(serializers.SlugRelatedField):
    """
    A SlugRelatedField that supports get_or_create.
    Used for creating or retrieving labels by name.
    """

    def to_representation(self, obj):
        return {"id": obj.id, "name": obj.name}

    # Overriding RelatedField.to_representation causes error in Browseable API
    # https://github.com/encode/django-rest-framework/issues/5141
    def get_choices(self, cutoff=None):
        queryset = self.get_queryset()
        if queryset is None:
            # Ensure that field.choices returns something sensible
            # even when accessed with a read-only field.
            return {}

        if cutoff is not None:
            queryset = queryset[:cutoff]

        return collections.OrderedDict(
            [
                (
                    # This is the only line that differs
                    # from the RelatedField's implementation
                    item.pk,
                    self.display_value(item),
                )
                for item in queryset
            ]
        )

    def to_internal_value(self, data):
        try:
            return self.get_queryset().get_or_create(**{self.slug_field: data})[0]
        except (TypeError, ValueError):
            self.fail("invalid")
