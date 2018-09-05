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
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from ara.api import models, serializers

from rest_framework import generics, status


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'labels': reverse('label-list', request=request, format=format),
        'playbooks': reverse('playbook-list', request=request, format=format),
        'plays': reverse('play-list', request=request, format=format),
        'tasks': reverse('task-list', request=request, format=format),
        'files': reverse('file-list', request=request, format=format),
        'hosts': reverse('host-list', request=request, format=format),
        'results': reverse('result-list', request=request, format=format),
        'stats': reverse('stats-list', request=request, format=format)
    })


class LabelList(generics.ListCreateAPIView):
    queryset = models.Label.objects.all()
    serializer_class = serializers.LabelSerializer


class LabelDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Label.objects.all()
    serializer_class = serializers.LabelSerializer


class PlaybookList(generics.ListCreateAPIView):
    queryset = models.Playbook.objects.all()
    serializer_class = serializers.PlaybookSerializer


class PlaybookDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Playbook.objects.all()
    serializer_class = serializers.PlaybookSerializer


class PlaybookFilesDetail(generics.CreateAPIView):
    queryset = models.Playbook.objects.all()
    serializer_class = serializers.FileSerializer

    def post(self, request, *args, **kwargs):
        playbook = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        playbook.files.add(serializer.data['id'])
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class PlayList(generics.ListCreateAPIView):
    queryset = models.Play.objects.all()
    serializer_class = serializers.PlaySerializer


class PlayDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Play.objects.all()
    serializer_class = serializers.PlaySerializer


class TaskList(generics.ListCreateAPIView):
    queryset = models.Task.objects.all()
    serializer_class = serializers.TaskSerializer


class TaskDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Task.objects.all()
    serializer_class = serializers.TaskSerializer


class HostList(generics.ListCreateAPIView):
    queryset = models.Host.objects.all()
    serializer_class = serializers.HostSerializer


class HostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Host.objects.all()
    serializer_class = serializers.HostSerializer


class ResultList(generics.ListCreateAPIView):
    queryset = models.Result.objects.all()
    serializer_class = serializers.ResultSerializer


class ResultDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Result.objects.all()
    serializer_class = serializers.ResultSerializer


class FileList(generics.ListCreateAPIView):
    queryset = models.File.objects.all()
    serializer_class = serializers.FileSerializer


class FileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.File.objects.all()
    serializer_class = serializers.FileSerializer


class StatsList(generics.ListCreateAPIView):
    queryset = models.Stats.objects.all()
    serializer_class = serializers.StatsSerializer


class StatsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Stats.objects.all()
    serializer_class = serializers.StatsSerializer
