# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django.conf import settings
from rest_framework import permissions


class APIAccessPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated if settings.READ_LOGIN_REQUIRED else True
        return request.user.is_authenticated if settings.WRITE_LOGIN_REQUIRED else True
