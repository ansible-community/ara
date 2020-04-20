#  Copyright (c) 2020 Red Hat, Inc.
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

import os

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(name="truncatepath")
@stringfilter
def truncatepath(path, count):
    """
    Truncates a path to less than 'count' characters.
    Paths are truncated on path separators.
    We prepend an ellipsis when we return a truncated path.
    """
    try:
        length = int(count)
    except ValueError:
        return path

    # Return immediately if there's nothing to truncate
    if len(path) < length:
        return path

    dirname, basename = os.path.split(path)
    while dirname:
        if len(dirname) + len(basename) < length:
            break
        dirlist = dirname.split("/")
        dirlist.pop(0)
        dirname = "/".join(dirlist)

    return "..." + os.path.join(dirname, basename)
