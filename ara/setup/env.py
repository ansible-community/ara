#  Copyright (c) 2019 Red Hat, Inc.
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

from __future__ import print_function

import os
from distutils.sysconfig import get_python_lib

from . import action_plugins, callback_plugins, lookup_plugins

exports = """
export ANSIBLE_CALLBACK_PLUGINS=${{ANSIBLE_CALLBACK_PLUGINS:-}}${{ANSIBLE_CALLBACK_PLUGINS+:}}{}
export ANSIBLE_ACTION_PLUGINS=${{ANSIBLE_ACTION_PLUGINS:-}}${{ANSIBLE_ACTION_PLUGINS+:}}{}
export ANSIBLE_LOOKUP_PLUGINS=${{ANSIBLE_LOOKUP_PLUGINS:-}}${{ANSIBLE_LOOKUP_PLUGINS+:}}{}
""".format(
    callback_plugins, action_plugins, lookup_plugins
)

if "VIRTUAL_ENV" in os.environ:
    """ PYTHONPATH may be exported when 'ara' module is installed in a
    virtualenv and ansible is installed on system python to avoid ansible
    failure to find ara module.
    """
    # inspired by https://stackoverflow.com/a/122340/99834
    lib = get_python_lib()
    if "PYTHONPATH" in os.environ:
        python_paths = os.environ["PYTHONPATH"].split(os.pathsep)
    else:
        python_paths = []
    if lib not in python_paths:
        python_paths.append(lib)
        exports += "export PYTHONPATH=${PYTHONPATH:-}${PYTHONPATH+:}%s\n" % os.pathsep.join(python_paths)

if __name__ == "__main__":
    print(exports.strip())
