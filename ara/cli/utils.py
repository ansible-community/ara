# Copyright (c) 2020 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import functools
import os


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
