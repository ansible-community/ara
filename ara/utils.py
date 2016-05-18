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

import os
import datetime
import json

from flask import url_for, Markup
from ara import app, models, db, LOG
from ara.config import ARA_PATH_MAX


@app.template_filter('datetime')
def jinja_date_formatter(timestamp, format='%Y-%m-%d %H:%M:%S'):
    """ Reformats a datetime timestamp from str(datetime.datetime)"""
    return datetime.datetime.strftime(timestamp, format)


@app.template_filter('to_nice_json')
def jinja_to_nice_json(result):
    """ Formats a result """
    return json.dumps(result, indent=4, sort_keys=True,
                      default=str)


@app.template_filter('from_json')
def jinja_from_json(val):
    try:
        return json.loads(val)
    except Exception as e:
        LOG.error('Unable to load json: %s' % str(e))
        return val


@app.template_filter('pathtruncate')
def jinja_pathtruncate(path):
    '''Truncates a path to less than ARA_PATH_MAX characters.  Paths
    are truncated on path separators.  We prepend an ellipsis when we
    return a truncated path.'''

    if path is None:
        return

    if len(path) < ARA_PATH_MAX:
        return path

    # always include the basename
    head, tail = os.path.split(path)
    newpath = tail

    while tail:
        if len(newpath) + len(tail) > ARA_PATH_MAX:
            break
        newpath = os.path.join(tail, newpath)
        head, tail = os.path.split(head)

    prefix = '...' if len(newpath) < len(path) else ''
    return os.path.join(prefix, newpath)


@app.context_processor
def ctx_add_nav_data():
    '''Makes some standard data from the database available in the
    template context.'''

    playbook_item_limit = app.config.get('NAV_MENU_MAX_PLAYBOOKS', 10)
    host_item_limit = app.config.get('NAV_MENU_MAX_HOSTS', 10)

    return dict(hosts=models.Host.query
                .order_by(models.Host.name)
                .limit(host_item_limit),
                playbooks=models.Playbook.query
                .order_by(models.Playbook.time_start.desc())
                .limit(playbook_item_limit))


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
