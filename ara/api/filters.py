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
from django.db import models as django_models

from ara.api import models as ara_models


class BaseFilter(django_filters.rest_framework.FilterSet):
    created_before = django_filters.IsoDateTimeFilter(field_name="created", lookup_expr="lte")
    created_after = django_filters.IsoDateTimeFilter(field_name="created", lookup_expr="gte")
    updated_before = django_filters.IsoDateTimeFilter(field_name="updated", lookup_expr="lte")
    updated_after = django_filters.IsoDateTimeFilter(field_name="updated", lookup_expr="gte")

    # fmt: off
    filter_overrides = {
        django_models.DateTimeField: {
            'filter_class': django_filters.IsoDateTimeFilter
        },
    }
    # fmt: on


class DateFilter(BaseFilter):
    started_before = django_filters.IsoDateTimeFilter(field_name="started", lookup_expr="lte")
    started_after = django_filters.IsoDateTimeFilter(field_name="started", lookup_expr="gte")
    ended_before = django_filters.IsoDateTimeFilter(field_name="ended", lookup_expr="lte")
    ended_after = django_filters.IsoDateTimeFilter(field_name="ended", lookup_expr="gte")


class LabelFilter(BaseFilter):
    # fmt: off
    order = django_filters.OrderingFilter(
        fields=(
            ("id", "id"),
            ("created", "created"),
            ("updated", "updated")
        )
    )
    # fmt: on


class PlaybookFilter(DateFilter):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    path = django_filters.CharFilter(field_name="path", lookup_expr="icontains")
    status = django_filters.MultipleChoiceFilter(
        field_name="status", choices=ara_models.Playbook.STATUS, lookup_expr="iexact"
    )
    label = django_filters.CharFilter(field_name="labels", lookup_expr="name__iexact")

    # fmt: off
    order = django_filters.OrderingFilter(
        fields=(
            ("id", "id"),
            ("created", "created"),
            ("updated", "updated"),
            ("started", "started"),
            ("ended", "ended"),
            ("duration", "duration"),
        )
    )
    # fmt: on


class PlayFilter(DateFilter):
    playbook = django_filters.NumberFilter(field_name="playbook__id", lookup_expr="exact")
    uuid = django_filters.UUIDFilter(field_name="uuid", lookup_expr="exact")
    status = django_filters.MultipleChoiceFilter(
        field_name="status", choices=ara_models.Play.STATUS, lookup_expr="iexact"
    )
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    # fmt: off
    order = django_filters.OrderingFilter(
        fields=(
            ("id", "id"),
            ("created", "created"),
            ("updated", "updated"),
            ("started", "started"),
            ("ended", "ended"),
            ("duration", "duration"),
        )
    )
    # fmt: on


class TaskFilter(DateFilter):
    playbook = django_filters.NumberFilter(field_name="playbook__id", lookup_expr="exact")
    status = django_filters.MultipleChoiceFilter(
        field_name="status", choices=ara_models.Task.STATUS, lookup_expr="iexact"
    )
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    action = django_filters.CharFilter(field_name="action", lookup_expr="iexact")
    path = django_filters.CharFilter(field_name="file__path", lookup_expr="icontains")

    # fmt: off
    order = django_filters.OrderingFilter(
        fields=(
            ("id", "id"),
            ("created", "created"),
            ("updated", "updated"),
            ("started", "started"),
            ("ended", "ended"),
            ("duration", "duration"),
        )
    )
    # fmt: on


class HostFilter(BaseFilter):
    playbook = django_filters.NumberFilter(field_name="playbook__id", lookup_expr="exact")
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    # fmt: off
    order = django_filters.OrderingFilter(
        fields=(
            ("id", "id"),
            ("created", "created"),
            ("updated", "updated"),
            ("name", "name"),
            ("changed", "changed"),
            ("failed", "failed"),
            ("ok", "ok"),
            ("skipped", "skipped"),
            ("unreachable", "unreachable"),
        )
    )
    # fmt: on


class ResultFilter(DateFilter):
    playbook = django_filters.NumberFilter(field_name="playbook__id", lookup_expr="exact")
    status = django_filters.MultipleChoiceFilter(
        field_name="status", choices=ara_models.Result.STATUS, lookup_expr="iexact"
    )
    ignore_errors = django_filters.BooleanFilter(field_name="ignore_errors", lookup_expr="exact")

    # fmt: off
    order = django_filters.OrderingFilter(
        fields=(
            ("id", "id"),
            ("created", "created"),
            ("updated", "updated"),
            ("started", "started"),
            ("ended", "ended"),
            ("duration", "duration"),
        )
    )
    # fmt: on


class FileFilter(BaseFilter):
    playbook = django_filters.NumberFilter(field_name="playbook__id", lookup_expr="exact")
    path = django_filters.CharFilter(field_name="path", lookup_expr="icontains")

    # fmt: off
    order = django_filters.OrderingFilter(
        fields=(
            ("id", "id"),
            ("created", "created"),
            ("updated", "updated"),
            ("path", "path")
        )
    )
    # fmt: on


class RecordFilter(BaseFilter):
    playbook = django_filters.NumberFilter(field_name="playbook__id", lookup_expr="exact")
    key = django_filters.CharFilter(field_name="key", lookup_expr="exact")

    # fmt: off
    order = django_filters.OrderingFilter(
        fields=(
            ("id", "id"),
            ("created", "created"),
            ("updated", "updated"),
            ("key", "key")
        )
    )
    # fmt: on
