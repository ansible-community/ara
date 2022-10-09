# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import glob
import os
from datetime import datetime

from django.utils.timezone import make_aware


def _human_readable_timestamp(seconds):
    """
    Translates a unix timestamp in seconds into something human readable.
    """
    timestamp = make_aware(datetime.fromtimestamp(seconds))
    return timestamp.strftime("%d %b %Y %H:%M:%S %z")


def _human_readable_size(size, decimal_places=2):
    """
    Translates a number of bytes from os.stat into something human readable.
    """
    for unit in ["B", "KiB", "MiB", "GiB", "TiB"]:
        if size < 1024.0:
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f}{unit}"


def find_distributed_databases(distributed_sqlite_root):
    """
    TODO: This approach can be slow, especially at scale if there are a lot of directories to look into.
          We should find a way to prevent crawling the filesystem each time, perhaps by doing it once and
          caching the results.
    """
    databases = glob.glob(f"{distributed_sqlite_root}/**/ansible.sqlite", recursive=True)
    data = []
    for db in databases:
        stat = os.stat(db)
        data.append(
            {
                "path": db.replace(f"{distributed_sqlite_root}/", ""),
                "size": _human_readable_size(stat.st_size),
                "updated": _human_readable_timestamp(stat.st_mtime),
            }
        )

    return data
