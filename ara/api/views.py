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

from rest_framework import viewsets

from ara.api import filters, models, serializers


class LabelViewSet(viewsets.ModelViewSet):
    queryset = models.Label.objects.all()
    filterset_class = filters.LabelFilter

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.ListLabelSerializer
        elif self.action == "retrieve":
            return serializers.DetailedLabelSerializer
        else:
            # create/update/destroy
            return serializers.LabelSerializer


class PlaybookViewSet(viewsets.ModelViewSet):
    filterset_class = filters.PlaybookFilter

    def get_queryset(self):
        statuses = self.request.GET.getlist("status")
        if statuses:
            return models.Playbook.objects.filter(status__in=statuses).order_by("-id")
        return models.Playbook.objects.all().order_by("-id")

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.ListPlaybookSerializer
        elif self.action == "retrieve":
            return serializers.DetailedPlaybookSerializer
        else:
            # create/update/destroy
            return serializers.PlaybookSerializer


class PlayViewSet(viewsets.ModelViewSet):
    filterset_class = filters.PlayFilter

    def get_queryset(self):
        statuses = self.request.GET.getlist("status")
        if statuses:
            return models.Play.objects.filter(status__in=statuses).order_by("-id")
        return models.Play.objects.all().order_by("-id")

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.ListPlaySerializer
        elif self.action == "retrieve":
            return serializers.DetailedPlaySerializer
        else:
            # create/update/destroy
            return serializers.PlaySerializer


class TaskViewSet(viewsets.ModelViewSet):
    filterset_class = filters.TaskFilter

    def get_queryset(self):
        statuses = self.request.GET.getlist("status")
        if statuses:
            return models.Task.objects.filter(status__in=statuses).order_by("-id")
        return models.Task.objects.all().order_by("-id")

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.ListTaskSerializer
        elif self.action == "retrieve":
            return serializers.DetailedTaskSerializer
        else:
            # create/update/destroy
            return serializers.TaskSerializer


class HostViewSet(viewsets.ModelViewSet):
    queryset = models.Host.objects.all()
    filterset_class = filters.HostFilter

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.ListHostSerializer
        elif self.action == "retrieve":
            return serializers.DetailedHostSerializer
        else:
            # create/update/destroy
            return serializers.HostSerializer


class ResultViewSet(viewsets.ModelViewSet):
    filterset_class = filters.ResultFilter

    def get_queryset(self):
        statuses = self.request.GET.getlist("status")
        if statuses:
            return models.Result.objects.filter(status__in=statuses).order_by("-id")
        return models.Result.objects.all().order_by("-id")

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.ListResultSerializer
        elif self.action == "retrieve":
            return serializers.DetailedResultSerializer
        else:
            # create/update/destroy
            return serializers.ResultSerializer


class FileViewSet(viewsets.ModelViewSet):
    queryset = models.File.objects.all()
    filterset_class = filters.FileFilter

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.ListFileSerializer
        elif self.action == "retrieve":
            return serializers.DetailedFileSerializer
        else:
            # create/update/destroy
            return serializers.FileSerializer


class RecordViewSet(viewsets.ModelViewSet):
    queryset = models.Record.objects.all()
    filterset_class = filters.RecordFilter

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.ListRecordSerializer
        elif self.action == "retrieve":
            return serializers.DetailedRecordSerializer
        else:
            # create/update/destroy
            return serializers.RecordSerializer
