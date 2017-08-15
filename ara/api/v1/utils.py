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
from flask_restful import fields
from oslo_utils import encodeutils


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


class Encoded(fields.Raw):
    def format(self, value):
        return encodeutils.safe_decode(value)


def encoded_input(value, argument='argument'):
    """ Returns an input safely encoded """
    if not isinstance(value, six.text_type):
        error = 'Invalid {arg}: {value}. {arg} must be a string.'
        raise ValueError(error.format(arg=argument, value=value))
    value = encodeutils.to_utf8(value)
    return value


def _field_to_string(field):
    # TODO: Revisit formatting values so that they're more friendly
    return str(field)
