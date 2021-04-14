# Copyright (c) 2021 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import pbr.version


def about(request):
    return {"ARA_VERSION": pbr.version.VersionInfo("ara").release_string()}
