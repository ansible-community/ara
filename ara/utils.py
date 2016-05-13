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

import datetime
import json

from ara import app, models, db
from flask import url_for, Markup


@app.template_filter('to_nice_json')
def jinja_to_nice_json(result):
    """ Formats a result """
    return json.dumps(result, indent=4, sort_keys=True,
                      default=str)


@app.template_filter('from_json')
def jinja_from_json(val):
    return json.loads(val)


@app.template_filter('pick_status')
def jinja_pick_status(row):
    """ Returns the status of a row """
    if row.changed:
        return 'CHANGED'
    if row.skipped:
        return 'SKIPPED'
    if row.failed:
        return 'FAILED'
    if row.unreachable:
        return 'UNREACHABLE'
    return 'OK'


def make_link(view, label, **kwargs):
    return Markup('<a href="{}">{}</a>'.format(
        url_for(view, **kwargs),
        label))


@app.context_processor
def ctx_add_utility_functions():
    '''Adds some utility functions to the template context.'''

    return dict(make_link=make_link)


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


def default_data():
    """
    Fetches a default set of data (mostly for displaying the top nav bar)
    """
    data = {
        'hosts': (
            r for (r,) in db.session.query(models.Host.name)),
        'playbooks': (
            r for (r,) in db.session.query(models.Playbook.path).distinct()),
    }

    return data


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


def status_to_query(status=None):
    """
    Returns a dict based on status
    """
    if status is not None:
        return {
            'ok': {
                'changed': 0,
                'failed': 0,
                'skipped': 0
            },
            'changed': {'changed': 1},
            'ignored': {
                'failed': 1,
                'ignore_errors': 1
            },
            'failed': {'failed': 1},
            'skipped': {'skipped': 1},
            'unreachable': {'unreachable': 1}
        }[status]
    else:
        return None


def get_tasks_for_playbooks(playbook_uuids, **kwargs):
    """
    Returns a dict containing all the tasks for a list of playbook uuids
    """
    data = {}
    for uuid in playbook_uuids:
        data[uuid] = models.Tasks.query.filter_by(playbook_uuid=uuid, **kwargs)

    return data


def get_stats_for_playbooks(playbook_uuids, **kwargs):
    """
    Returns a dict containing all the stats for a list of playbook uuids
    """
    data = {}
    for uuid in playbook_uuids:
        data[uuid] = models.Stats.query.filter_by(playbook_uuid=uuid, **kwargs)

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
