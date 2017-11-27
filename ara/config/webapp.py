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

import xstatic.main
import xstatic.pkg.bootstrap_scss
import xstatic.pkg.datatables
import xstatic.pkg.jquery
import xstatic.pkg.patternfly
import xstatic.pkg.patternfly_bootstrap_treeview
from ara.config.compat import ara_config
from ara.config.logger import ARA_LOG_LEVEL

ARA_ENABLE_DEBUG_VIEW = True if ARA_LOG_LEVEL == 'DEBUG' else False

ARA_PLAYBOOK_PER_PAGE = ara_config('playbook_per_page',
                                   'ARA_PLAYBOOK_PER_PAGE',
                                   10,
                                   value_type='integer')
ARA_RESULT_PER_PAGE = ara_config('result_per_page',
                                 'ARA_RESULT_PER_PAGE',
                                 25,
                                 value_type='integer')

treeview = xstatic.pkg.patternfly_bootstrap_treeview
XSTATIC = dict(
    bootstrap=xstatic.main.XStatic(xstatic.pkg.bootstrap_scss).base_dir,
    datatables=xstatic.main.XStatic(xstatic.pkg.datatables).base_dir,
    jquery=xstatic.main.XStatic(xstatic.pkg.jquery).base_dir,
    patternfly=xstatic.main.XStatic(xstatic.pkg.patternfly).base_dir,
    patternfly_bootstrap_treeview=xstatic.main.XStatic(treeview).base_dir,
)
