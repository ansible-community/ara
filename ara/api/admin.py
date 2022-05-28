# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django.contrib import admin
from django.contrib.auth.models import Group

from ara.api import models


class RecordAdmin(admin.ModelAdmin):
    list_display = ("id", "key", "value", "type")
    search_fields = ("key", "value", "type")
    ordering = ("key",)


admin.site.register(models.Record, RecordAdmin)
admin.site.unregister(Group)
