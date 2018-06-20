from ara.api import models
from django.contrib import admin
from django.contrib.auth.models import Group


class RecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'key', 'value', 'type')
    search_fields = ('key', 'value', 'type')
    ordering = ('key',)


admin.site.register(models.Record, RecordAdmin)
admin.site.unregister(Group)
