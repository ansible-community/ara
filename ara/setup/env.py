# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import print_function

import os
from sysconfig import get_path

from . import action_plugins, callback_plugins, lookup_plugins

exports = """
export ANSIBLE_CALLBACK_PLUGINS=${{ANSIBLE_CALLBACK_PLUGINS:-}}${{ANSIBLE_CALLBACK_PLUGINS+:}}{}
export ANSIBLE_ACTION_PLUGINS=${{ANSIBLE_ACTION_PLUGINS:-}}${{ANSIBLE_ACTION_PLUGINS+:}}{}
export ANSIBLE_LOOKUP_PLUGINS=${{ANSIBLE_LOOKUP_PLUGINS:-}}${{ANSIBLE_LOOKUP_PLUGINS+:}}{}
""".format(
    callback_plugins, action_plugins, lookup_plugins
)

if "VIRTUAL_ENV" in os.environ:
    """PYTHONPATH may be exported when 'ara' module is installed in a
    virtualenv and ansible is installed on system python to avoid ansible
    failure to find ara module.
    """
    # inspired by https://stackoverflow.com/a/122340/99834
    lib = get_path("purelib")
    if "PYTHONPATH" in os.environ:
        python_paths = os.environ["PYTHONPATH"].split(os.pathsep)
    else:
        python_paths = []
    if lib not in python_paths:
        python_paths.append(lib)
        exports += "export PYTHONPATH=${PYTHONPATH:-}${PYTHONPATH+:}%s\n" % os.pathsep.join(python_paths)

if __name__ == "__main__":
    print(exports.strip())
