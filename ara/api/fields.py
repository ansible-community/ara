#  Copyright (c) 2019 Red Hat, Inc.
#
#  This file is part of ARA Records Ansible.
#
#  ARA Records Ansible is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  ARA Records Ansible is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with ARA Records Ansible. If not, see <http://www.gnu.org/licenses/>.

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
