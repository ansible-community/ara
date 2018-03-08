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

from api import models, serializers

from rest_framework import viewsets


class PlaybookViewSet(viewsets.ModelViewSet):
    queryset = models.Playbook.objects.all()
    serializer_class = serializers.PlaybookSerializer


class PlayViewSet(viewsets.ModelViewSet):
    queryset = models.Play.objects.all()
    serializer_class = serializers.PlaySerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = models.Task.objects.all()
    serializer_class = serializers.TaskSerializer


class HostViewSet(viewsets.ModelViewSet):
    queryset = models.Host.objects.all()
    serializer_class = serializers.HostSerializer


class ResultViewSet(viewsets.ModelViewSet):
    queryset = models.Result.objects.all()
    serializer_class = serializers.ResultSerializer


class RecordViewSet(viewsets.ModelViewSet):
    queryset = models.Record.objects.all()
    serializer_class = serializers.RecordSerializer


class FileViewSet(viewsets.ModelViewSet):
    queryset = models.File.objects.all()
    serializer_class = serializers.FileSerializer
