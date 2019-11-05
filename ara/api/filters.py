#  Copyright (c) 2019 Red Hat, Inc.
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

import django_filters


class PlaybookFilter(django_filters.rest_framework.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="iexact")
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")


class PlayFilter(django_filters.rest_framework.FilterSet):
    playbook = django_filters.NumberFilter(field_name="playbook__id", lookup_expr="exact")
    uuid = django_filters.UUIDFilter(field_name="uuid", lookup_expr="exact")


class TaskFilter(django_filters.rest_framework.FilterSet):
    playbook = django_filters.NumberFilter(field_name="playbook__id", lookup_expr="exact")


class HostFilter(django_filters.rest_framework.FilterSet):
    playbook = django_filters.NumberFilter(field_name="playbook__id", lookup_expr="exact")


class ResultFilter(django_filters.rest_framework.FilterSet):
    playbook = django_filters.NumberFilter(field_name="playbook__id", lookup_expr="exact")


class FileFilter(django_filters.rest_framework.FilterSet):
    playbook = django_filters.NumberFilter(field_name="playbook__id", lookup_expr="exact")
    path = django_filters.CharFilter(field_name="path", lookup_expr="exact")


class RecordFilter(django_filters.rest_framework.FilterSet):
    playbook = django_filters.NumberFilter(field_name="playbook__id", lookup_expr="exact")
    key = django_filters.CharFilter(field_name="key", lookup_expr="exact")
