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
