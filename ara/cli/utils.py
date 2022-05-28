# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import functools
import os
from datetime import datetime, timedelta


@functools.lru_cache(maxsize=10)
def get_playbook(client, playbook_id):
    playbook = client.get("/api/v1/playbooks/%s" % playbook_id)
    return playbook


@functools.lru_cache(maxsize=10)
def get_play(client, play_id):
    play = client.get("/api/v1/plays/%s" % play_id)
    return play


@functools.lru_cache(maxsize=10)
def get_task(client, task_id):
    task = client.get("/api/v1/tasks/%s" % task_id)
    return task


@functools.lru_cache(maxsize=10)
def get_host(client, host_id):
    host = client.get("/api/v1/hosts/%s" % host_id)
    return host


def parse_timedelta(duration: str, pattern: str = "%H:%M:%S.%f"):
    """Parses a timedelta string back into a timedelta object"""
    parsed = datetime.strptime(duration, pattern)
    # fmt: off
    return timedelta(
        hours=parsed.hour,
        minutes=parsed.minute,
        seconds=parsed.second,
        microseconds=parsed.microsecond
    ).total_seconds()
    # fmt: on


def sum_timedelta(duration: str, total: float):
    """
    Returns the sum of two timedeltas as provided by the API, for example:
    00:00:02.031557 + 00:00:04.782581 = ?
    """
    return parse_timedelta(duration) + total


def avg_timedelta(delta: timedelta, count: int):
    """Returns an average timedelta based on the amount of occurrences"""
    return str(delta / count)


# Also see: ui.templatetags.truncatepath
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
