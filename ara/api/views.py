# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

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

    def perform_destroy(self, instance):
        """
        Update the LatestHost table when deleting a playbook (if necessary)
        """
        # check if Host object has a relation to a LatestHost object
        for host in instance.hosts.all():
            try:
                latest = models.LatestHost.objects.get(host=host.id)
            except models.LatestHost.DoesNotExist:
                # No need to delete the host, the cascade will take care of it
                continue

            # Find the next-latest host that isn't this one
            next_latest = models.Host.objects.filter(name=host.name).order_by("-updated")

            if len(next_latest) > 1:
                latest.host = next_latest[1]
                latest.save()

        return super().perform_destroy(instance)


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

    def perform_destroy(self, instance):
        """
        Update the LatestHost table when deleting a host (if necessary)
        """
        # check if Host object has a relation to a LatestHost object
        try:
            latest = models.LatestHost.objects.get(host=instance.id)
        except models.LatestHost.DoesNotExist:
            return super().perform_destroy(instance)

        # Find the next-latest host that isn't this one
        next_latest = models.Host.objects.filter(name=instance.name).order_by("-updated")

        if len(next_latest) > 1:
            latest.host = next_latest[1]
            latest.save()

        return super().perform_destroy(instance)

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.ListHostSerializer
        elif self.action == "retrieve":
            return serializers.DetailedHostSerializer
        else:
            # create/update/destroy
            return serializers.HostSerializer


class LatestHostViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.LatestHost.objects.all()
    filterset_class = filters.LatestHostFilter
    serializer_class = serializers.DetailedLatestHostSerializer


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
