#   Copyright 2016 Red Hat, Inc. All Rights Reserved.
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

import json
from collections import defaultdict
from ara import models


def fields_from_iter(fields, items, xforms=None):
    '''Returns column headers and data for use by
    `cliff.lister.Lister`.  In this function and in
    `fields_from_object`, fields are specified as a list of
    `(column_name, object_path)` tuples.  The `object_path` can be
    omitted if it can be inferred from the column name by converting
    the name to lowercase and converting ' ' to '_'.  For example:

        fields = (
            ('ID',),
            ('Name',),
            ('Playbook',),
        )

    The `xforms` parameter is a dictionary maps column names to
    callables that will be used to format the corresponding value.
    For example:

        xforms = {
            'Playbook': lambda p: p.name,
        }
    '''

    xforms = xforms or {}

    return (zip(*fields)[0], [
        [xform(v) for v, xform in
         [(get_field_attr(item, f[0]), f[1]) for f in
          [(field, xforms.get(field[0], lambda x: x)) for field in fields]]]
        for item in items])


def fields_from_object(fields, obj, xforms=None):
    '''Returns labels and values for use by `cliff.show.ShowOne`.  See
    the documentation for `fields_from_iter` for details.'''

    xforms = xforms or {}

    return (zip(*fields)[0],
            [xform(v) for v, xform in
             [(get_field_attr(obj, f[0]), f[1]) for f in
              [(field, xforms.get(field[0], lambda x: x))
               for field in fields]]])


def status_to_query(status):
    """
    Returns a dict to be used as filter kwargs based on status
    """
    if status == 'changed':
        return {
            'status': 'ok',
            'changed': True,
        }
    else:
        return {
            'status': status,
        }


def get_host_playbook_stats(host_obj):
    '''Returns a dictionary that contains statistics for each playbook
    where the host in host_obj is involved. If there are no statistics for
    the playbook for that host (i.e, interrupted playbook run), we return 'n/a'
    as statistics.
    '''

    data = {}
    playbooks = host_obj.playbooks
    stats = host_obj.stats
    for playbook in playbooks:
        data[playbook.id] = defaultdict(lambda: 'n/a')
        try:
            data[playbook.id] = stats.filter_by(playbook_id=playbook.id).one()
        except models.NoResultFound:
            pass
    return data


def get_summary_stats(items, attr):
    '''Returns a dictionary of aggregated statistics for `items` filtered by
    `attr`. For example, it will aggregate statistics for a host across all
    the playbook runs it has been a member of, with the following structure:

        data[host.id] = {
            'ok': 4
            'changed': 4
            ...
        }
    '''

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
    return data


def get_field_attr(obj, field):
    '''Returns the value of an attribute path applied to an object.
    The attribute path is either made available explicitly as
    `field[1]` or implicitly by converting `field[0]` to lower case
    and converting ' ' to '_'.  In other words, given:

        field = ('Name',)

    `get_field_attribute(obj, field)` would return the value of the
    `name` attribute of `obj`.  On other hand, given:

        field = ('Name', 'playbook.name')

    `get_field_attribute(obj, field)` would return the value of the
    `name` attribute of the `playbook` attribute of `obj`.
    '''

    path = field[-1].lower().replace(' ', '_').split('.')
    return reduce(getattr, path, obj)


def format_json(val):
    try:
        return json.dumps(json.loads(val),
                          indent=4,
                          sort_keys=True,
                          default=str)
    except (TypeError, ValueError):
        return val
