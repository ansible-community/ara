#  Copyright (c) 2018 Red Hat, Inc.
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

import os

# The path where ARA is installed (parent directory)
path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

plugins = os.path.abspath(os.path.join(path, "plugins"))
action_plugins = os.path.abspath(os.path.join(plugins, "action"))
callback_plugins = os.path.abspath(os.path.join(plugins, "callback"))
lookup_plugins = os.path.abspath(os.path.join(plugins, "lookup"))
