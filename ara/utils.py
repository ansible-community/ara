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

from ara import models
from oslo_serialization import jsonutils
from oslo_utils import encodeutils
from sqlalchemy import func

import hashlib
import pyfakefs.fake_filesystem as fake_filesystem


def generate_identifier(result):
    """
    Returns a fixed length identifier based on a hash of a combined set of
    playbook/task values which are as close as we can guess to unique for each
    task.
    """
    # Determine the playbook file path to use for the ID
    if result.task.playbook and result.task.playbook.path:
        playbook_file = result.task.playbook.path
    else:
        playbook_file = ''
    play_path = u'%s.%s' % (playbook_file, result.task.play.name)

    # Determine the task file path to use for the ID
    if result.task.file and result.task.file.path:
        task_file = result.task.file.path
    else:
        task_file = ''
    task_path = u'%s.%s' % (task_file, result.task.name)

    # Combine both of the above for a full path
    identifier_path = u'%s.%s' % (play_path, task_path)

    # Assign the identifier as a hash of the fully unique path.
    identifier = hashlib.sha1(encodeutils.to_utf8(identifier_path)).hexdigest()

    return identifier


def get_summary_stats(items, attr):
    """
    Returns a dictionary of aggregated statistics for 'items' filtered by
    "attr'. For example, it will aggregate statistics for a host across all
    the playbook runs it has been a member of, with the following structure:

        data[host.id] = {
            'ok': 4
            'changed': 4
            ...
        }
    """
    data = {}
    for item in items:
        stats = models.Stats.query.filter_by(**{attr: item.id})
        data[item.id] = {
            'ok': sum([int(stat.ok) for stat in stats]),
            'changed': sum([int(stat.changed) for stat in stats]),
            'failed': sum([int(stat.failed) for stat in stats]),
            'skipped': sum([int(stat.skipped) for stat in stats]),
            'unreachable': sum([int(stat.unreachable) for stat in stats])
        }

        # If we're aggregating stats for a playbook, also infer status
        if attr is "playbook_id":
            data[item.id]['status'] = _infer_status(item, data[item.id])

    return data


def _infer_status(playbook, playbook_stats):
    """
    Infer the status of a playbook run based on it's statistics or completion
    """
    if not playbook.complete:
        return 'incomplete'

    if playbook_stats['failed'] >= 1 or playbook_stats['unreachable'] >= 1:
        return 'failed'
    else:
        return 'success'


def fast_count(query):
    """
    It turns out the built-in SQLAlchemy function for query.count() is pretty
    slow. Alternatively, use this optimized function instead.
    """
    count_query = (query
                   .statement.with_only_columns([func.count()]).order_by(None))
    count = query.session.execute(count_query).scalar()
    return count


def generate_tree(root, paths, mock_os):
    """
    Given a file path, returns a JSON structure suitable for bootstrap-treeview
    mock_os represents a faked filesystem generated from the playbook_treeview
    method.
    Credit: Mohammed Naser & David Moreau Simard
    """
    tree = []
    dentries = mock_os.listdir(root)

    for d in dentries:
        full_path = mock_os.path.join(root, d)
        node = {
            'text': d,
            'href': '#%s' % d,
            'state': {
                'expanded': True
            }
        }

        if mock_os.path.isdir(full_path):
            node['nodes'] = generate_tree(full_path, paths, mock_os)
        else:
            node['icon'] = 'fa fa-file-code-o'
            node['href'] = '#'
            node['color'] = '#0088ce'
            node['dataAttr'] = {
                'toggle': 'modal',
                'target': '#file_modal',
                'load': paths[full_path] + '/'
            }
        tree.append(node)
    return tree


def playbook_treeview(playbook):
    """
    Creates a fake filesystem with playbook files and uses generate_tree() to
    recurse and return a JSON structure suitable for bootstrap-treeview.
    """
    fs = fake_filesystem.FakeFilesystem()
    mock_os = fake_filesystem.FakeOsModule(fs)

    files = models.File.query.filter(models.File.playbook_id.in_([playbook]))

    paths = {}
    for file in files:
        fs.CreateFile(file.path)
        paths[file.path] = file.id

    return jsonutils.dumps(generate_tree('/', paths, mock_os),
                           sort_keys=True,
                           indent=2)
