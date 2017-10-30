#  Copyright (c) 2017 Red Hat, Inc.
#
#  This file is part of ARA: Ansible Run Analysis.
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

import six
from flask import url_for
from flask import request
from flask_restful import fields
from oslo_utils import encodeutils
from oslo_serialization import jsonutils

try:
    from urlparse import urlparse, urlunparse
except ImportError:
    # python3
    from urllib.parse import urlparse, urlunparse


def help(args, fields):
    arguments = {
        arg.name: {
            'type': str(arg.type),
            'required': arg.required,
            'default': arg.default,
            'help': arg.help,
        }
        for arg in args
    }
    output = {
        key: _field_to_string(value)
        for key, value in fields.items()
    }
    return {
        'query_parameters': arguments,
        'result_output': output,
    }


class ResourceUrl(fields.Raw):
    """
    A string representation of a Url for a resource, for example
    /api/<resource>/<id>/<items>
    :param endpoint: Endpoint name. If endpoint is ``None``,
        ``request.endpoint`` is used instead
    :type endpoint: str
    :param absolute: If ``True``, ensures that the generated urls will have the
        hostname included
    :type absolute: bool
    :param scheme: URL scheme specifier (e.g. ``http``, ``https``)
    :type scheme: str
    """
    def __init__(self, endpoint=None, absolute=False, scheme=None,
                 resource=None, **kwargs):
        super(ResourceUrl, self).__init__(**kwargs)
        self.endpoint = endpoint
        self.absolute = absolute
        self.scheme = scheme
        self.resource = resource

    def output(self, key, obj):
        try:
            data = fields.to_marshallable_type(obj)
            endpoint = self.endpoint or request.endpoint
            o = urlparse(url_for(endpoint, _external=self.absolute, **data))
            path = "%s/%s" % (o.path, self.resource)
            if self.absolute:
                scheme = self.scheme or o.scheme
                return urlunparse((scheme, o.netloc, path, "", "", ""))
            return urlunparse(("", "", path, "", "", ""))
        except TypeError as te:
            raise fields.MarshallingException(te)


class Encoded(fields.Raw):
    def format(self, value):
        return encodeutils.safe_decode(value)


def encoded_input(value, argument='argument'):
    """ Returns an input safely encoded """
    if not isinstance(value, six.text_type):
        error = 'Invalid {arg}: {value}. {arg} must be a string.'
        raise ValueError(error.format(arg=argument, value=value))
    return encodeutils.safe_decode(value)


def result_input(value, argument='argument'):
    """
    Returns either a dict for a single result or or a list of dicts for many
    results.
    """
    try:
        value = jsonutils.loads(jsonutils.dumps(value))
        return value
    except (ValueError, TypeError) as e:
        error = 'Unable to load JSON from {arg}: {exc}'
        raise ValueError(error.format(arg=argument, exc=six.text_type(e)))


def _field_to_string(field):
    # TODO: Revisit formatting values so that they're more friendly
    return str(field)
