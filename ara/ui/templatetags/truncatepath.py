# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

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

    if "/" not in path:
        # Non-paths look better with the end cut off
        return path[: length - 4] + "..."

    dirname, basename = os.path.split(path)

    if len(basename) >= length:
        # fmt: off
        return "..." + basename[4 - length:]
        # fmt: on

    while dirname:
        if len(dirname) + len(basename) + 4 < length:
            break
        dirlist = dirname.split("/")
        dirlist.pop(0)
        dirname = "/".join(dirlist)

    return "..." + os.path.join(dirname, basename)
