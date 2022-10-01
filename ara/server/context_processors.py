# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from ara.setup import ara_version as ARA_VERSION


def about(request):
    return {"ARA_VERSION": ARA_VERSION}
