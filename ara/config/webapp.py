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

from xstatic import main as xs
import xstatic.pkg.bootstrap_scss
import xstatic.pkg.datatables
import xstatic.pkg.jquery
import xstatic.pkg.patternfly
import xstatic.pkg.patternfly_bootstrap_treeview
from ara.config.compat import ara_config


class WebAppConfig(object):
    def __init__(self):
        self.ARA_PLAYBOOK_PER_PAGE = ara_config(
            'playbook_per_page',
            'ARA_PLAYBOOK_PER_PAGE',
            10,
            value_type='integer'
        )
        self.ARA_RESULT_PER_PAGE = ara_config(
            'result_per_page',
            'ARA_RESULT_PER_PAGE',
            25,
            value_type='integer'
        )
        self.ARA_PLAYBOOK_OVERRIDE = ara_config(
            'playbook_override',
            'ARA_PLAYBOOK_OVERRIDE',
            None,
            value_type='list'
        )

        treeview = xstatic.pkg.patternfly_bootstrap_treeview
        self.XSTATIC = dict(
            bootstrap=xs.XStatic(xstatic.pkg.bootstrap_scss).base_dir,
            datatables=xs.XStatic(xstatic.pkg.datatables).base_dir,
            jquery=xs.XStatic(xstatic.pkg.jquery).base_dir,
            patternfly=xs.XStatic(xstatic.pkg.patternfly).base_dir,
            patternfly_bootstrap_treeview=xs.XStatic(treeview).base_dir,
        )

    @property
    def config(self):
        """ Returns a dictionary for the loaded configuration """
        return {
            key: self.__dict__[key]
            for key in dir(self)
            if key.isupper()
        }
