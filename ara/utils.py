#   Copyright 2017 Red Hat, Inc. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

from ara import models
from sqlalchemy import func
import json
import pyfakefs.fake_filesystem as fake_filesystem


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
                'load': paths[full_path]
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

    return json.dumps(generate_tree('/', paths, mock_os),
                      sort_keys=True,
                      indent=2)
