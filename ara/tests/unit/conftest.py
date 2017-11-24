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

# These fixtures are automatically loaded by pytest
# https://docs.pytest.org/en/latest/fixture.html

import os
import pytest
import shlex
import shutil
import subprocess
import tempfile
from ara.setup import path as ara_location


def ansible(env, inventory, playbook, verbose=False):
    """
    Wrapper function to run an ansible-playbook command
    """
    command = 'ansible-playbook -i %s %s' % (inventory, playbook)
    if verbose:
        command += ' -vvv'

    try:
        output = subprocess.check_output(shlex.split(command),
                                         env=env,
                                         stderr=subprocess.PIPE)
        exception = False
    except subprocess.CalledProcessError as e:
        # We'll re-raise the exception later but retrieve the output first
        output = e.output
        exception = e

    return exception, output


@pytest.fixture(scope='module')
def run_ansible_env(request, inventory='default',
                    playbook='smoke.yml',
                    database=None):
    """
    Runs a set of playbooks once with ARA enabled with environment variables.
    """
    # Create and destroy a temporary directory for each run
    tmpdir = tempfile.mkdtemp(prefix='ara_')
    request.addfinalizer(lambda: shutil.rmtree(tmpdir))

    # If no database was specified (i.e, mysql+pymysql://, default to sqlite)
    if database is None:
        # Default to sqlite
        handle, database = tempfile.mkstemp(suffix='.sqlite', dir=tmpdir)
        database = 'sqlite:///%s' % database

    # Environment variables we'll be passing to ansible-playbook subprocess
    config = {
        'ARA_DATABASE': database,
        'ARA_DIR': tmpdir
    }
    env = os.environ.copy()
    env.update(config)
    env.update({
        'ANSIBLE_RETRY_FILES_ENABLED': 'False',
        'ANSIBLE_CALLBACK_PLUGINS': '%s/plugins/callbacks' % ara_location,
        'ANSIBLE_ACTION_PLUGINS': '%s/plugins/actions' % ara_location,
        'ANSIBLE_LIBRARY': '%s/plugins/modules' % ara_location
    })

    # Path to inventory and playbook we'll be using
    fixtures = os.path.join(ara_location, 'tests/fixtures')
    inventory = os.path.join(fixtures, 'inventory/%s' % inventory)
    playbook = os.path.join(fixtures, playbook)

    # If pytest is verbose, make Ansible verbose
    verbose = False
    if request.config.getoption('verbose') > 0:
        verbose = True

    # Run Ansible and catch non-zero exits
    exception, output = ansible(env, inventory, playbook, verbose)
    if exception:
        print(output)
        raise exception
    print(output)

    yield {
        'output': output,
        'env': env,
        'inventory': inventory,
        'playbook': playbook
    }


@pytest.fixture(scope='module')
def run_ansible_cfg(request):
    """
    Runs a set of playbooks once with ARA enabled with ansible.cfg.
    """
    pass
