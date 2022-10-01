# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import os

import pbr.version

ara_version = pbr.version.VersionInfo("ara").release_string()

# The path where ARA is installed (parent directory)
path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

plugins = os.path.abspath(os.path.join(path, "plugins"))
action_plugins = os.path.abspath(os.path.join(plugins, "action"))
callback_plugins = os.path.abspath(os.path.join(plugins, "callback"))
lookup_plugins = os.path.abspath(os.path.join(plugins, "lookup"))
