# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import hashlib
import json
import zlib


def compressed_obj(obj):
    """
    Returns a zlib compressed representation of an object
    """
    return zlib.compress(json.dumps(obj).encode("utf-8"))


def compressed_str(obj):
    """
    Returns a zlib compressed representation of a string
    """
    return zlib.compress(obj.encode("utf-8"))


def sha1(obj):
    """
    Returns the sha1 of a compressed string or an object
    """
    return hashlib.sha1(obj.encode("utf8")).hexdigest()
