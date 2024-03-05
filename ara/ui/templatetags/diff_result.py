# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import difflib
import json

from django import template

register = template.Library()


def render_diff(before="", after="", prepared="", before_header="before", after_header="after"):
    """
    Renders a diff provided by Ansible task results
    """
    # fmt: off
    if prepared:
        # Modules like apt, git or ios/eos provide pre-generated diff as string
        return prepared.splitlines()
    elif isinstance(before, dict) and isinstance(after, dict):
        # Some modules, such as file, might provide a diff in a dict format
        return difflib.unified_diff(
            json.dumps(before, indent=4).splitlines(),
            json.dumps(after, indent=4).splitlines(),
            fromfile=before_header,
            tofile=after_header
        )
    else:
        return difflib.unified_diff(
            before.splitlines(),
            after.splitlines(),
            fromfile=before_header,
            tofile=after_header
        )
    # fmt: on


@register.filter(name="diff_result")
def diff_result(diff):
    """
    Renders a diff (or a list of diffs) provided by Ansible task results
    """
    diffs = []

    # Modules are free to provide their own diff key which might not respect the convention set by modules such
    # as "file", "ini_file", "lineinfile, "template" or "copy" causing a parsing failure.
    # If that happens, give up and return value as it was provided so we don't raise an
    # exception/internal server error.
    try:
        if isinstance(diff, list):
            diffs = [render_diff(**result) for result in diff]
        elif isinstance(diff, dict):
            diffs = [render_diff(**diff)]
    except (TypeError, AttributeError):
        return diff

    # The unified diff is a generator, we need to iterate through it to return
    # the entire diff.
    lines = []
    for d in diffs:
        for line in d:
            lines.append(line)

    return "\n".join(lines)
