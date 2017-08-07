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


def _field_to_string(field):
    # TODO: Revisit formatting values so that they're more friendly
    return str(field)
