# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import print_function

from . import action_plugins, callback_plugins, lookup_plugins

config = """
[defaults]
callback_plugins={}
action_plugins={}
lookup_plugins={}
""".format(
    callback_plugins, action_plugins, lookup_plugins
)

if __name__ == "__main__":
    print(config.strip())
