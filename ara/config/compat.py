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

from ansible import __version__ as ansible_version
from ansible.constants import get_config
try:
    from ansible.constants import load_config_file
except ImportError:
    # Ansible 2.4 no longer provides load_config_file, this is handled further
    # down
    from ansible.config.manager import find_ini_config_file
    # Also, don't scream deprecated things at us
    import ansible.constants
    ansible.constants._deprecated = lambda *args: None
from distutils.version import LooseVersion
from six.moves import configparser


def ara_config(key, env_var, default, section='ara', value_type=None):
    """
    Wrapper around Ansible's get_config backward/forward compatibility
    """
    # Bootstrap Ansible configuration
    # Ansible >=2.4 takes care of loading the configuration file itself
    if LooseVersion(ansible_version) < LooseVersion('2.4.0'):
        config, path = load_config_file()
    else:
        path = find_ini_config_file()
        config = configparser.ConfigParser()
        if path is not None:
            config.read(path)

    # >= 2.3.0.0 (NOTE: Ansible trunk versioning scheme has 3 digits, not 4)
    if LooseVersion(ansible_version) >= LooseVersion('2.3.0'):
        return get_config(config, section, key, env_var, default,
                          value_type=value_type)

    # < 2.3.0.0 compatibility
    if value_type is None:
        return get_config(config, section, key, env_var, default)

    args = {
        'boolean': dict(boolean=True),
        'integer': dict(integer=True),
        'list': dict(islist=True),
        'tmppath': dict(istmppath=True)
    }
    return get_config(config, section, key, env_var, default,
                      **args[value_type])
