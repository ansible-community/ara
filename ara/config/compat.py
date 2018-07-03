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

# Compatibility layer between ARA and the different version of Ansible

from ansible.constants import get_config
from ansible.config.manager import find_ini_config_file
import ansible.constants
from six.moves import configparser

# Please don't scream deprecated warnings at us
ansible.constants._deprecated = lambda *args: None


def ara_config(key, env_var, default, section='ara', value_type=None):
    """
    Wrapper around Ansible's get_config backward/forward compatibility
    """
    # Bootstrap Ansible configuration
    # Ansible >=2.4 takes care of loading the configuration file itself
    path = find_ini_config_file()
    config = configparser.ConfigParser()
    if path is not None:
        config.read(path)

    return get_config(
        config, section, key, env_var, default, value_type=value_type
    )
