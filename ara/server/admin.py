# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django.contrib import admin


class AraAdminSite(admin.AdminSite):
    site_header = "Administration"
    index_title = "Administration Ara"
