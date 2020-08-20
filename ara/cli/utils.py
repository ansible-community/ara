# Copyright (c) 2020 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import functools


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
