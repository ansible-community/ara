import codecs

from rest_framework import generics
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

from ara.api import filters, models, serializers
from ara.ui import forms
from ara.ui.pagination import LimitOffsetPaginationWithLinks


class Index(generics.ListAPIView):
    """
    Returns a list of playbook summaries
    """

    queryset = models.Playbook.objects.all()
    filterset_class = filters.PlaybookFilter
    renderer_classes = [TemplateHTMLRenderer]
    pagination_class = LimitOffsetPaginationWithLinks
    template_name = "index.html"

    def get(self, request, *args, **kwargs):
        search_form = forms.PlaybookSearchForm(request.GET)

        query = self.filter_queryset(self.queryset.all().order_by("-id"))
        page = self.paginate_queryset(query)
        if page is not None:
            serializer = serializers.ListPlaybookSerializer(page, many=True)
        else:
            serializer = serializers.ListPlaybookSerializer(query, many=True)
        response = self.get_paginated_response(serializer.data)

        if self.paginator.count > (self.paginator.offset + self.paginator.limit):
            max_current = self.paginator.offset + self.paginator.limit
        else:
            max_current = self.paginator.count
        current_page_results = "%s-%s" % (self.paginator.offset + 1, max_current)

        return Response(
            {
                "page": "index",
                "data": response.data,
                "search_form": search_form,
                "current_page_results": current_page_results,
            }
        )


class Playbook(generics.RetrieveAPIView):
    """
    Returns a page for a detailed view of a playbook
    """

    queryset = models.Playbook.objects.all()
    renderer_classes = [TemplateHTMLRenderer]
    pagination_class = LimitOffsetPaginationWithLinks
    template_name = "playbook.html"

    def get(self, request, *args, **kwargs):
        playbook = serializers.DetailedPlaybookSerializer(self.get_object())
        hosts = serializers.ListHostSerializer(
            models.Host.objects.filter(playbook=playbook.data["id"]).order_by("name").all(), many=True
        )
        files = serializers.ListFileSerializer(
            models.File.objects.filter(playbook=playbook.data["id"]).all(), many=True
        )
        records = serializers.ListRecordSerializer(
            models.Record.objects.filter(playbook=playbook.data["id"]).all(), many=True
        )

        search_form = forms.ResultSearchForm(request.GET)
        order = "-started"
        if "order" in request.GET:
            order = request.GET["order"]
        result_queryset = models.Result.objects.filter(playbook=playbook.data["id"]).order_by(order).all()
        result_filter = filters.ResultFilter(request.GET, queryset=result_queryset)

        page = self.paginate_queryset(result_filter.qs)
        if page is not None:
            serializer = serializers.ListResultSerializer(page, many=True)
        else:
            serializer = serializers.ListResultSerializer(result_filter, many=True)

        for result in serializer.data:
            task_id = result["task"]
            result["task"] = serializers.SimpleTaskSerializer(models.Task.objects.get(pk=task_id)).data
            host_id = result["host"]
            result["host"] = serializers.SimpleHostSerializer(models.Host.objects.get(pk=host_id)).data
        paginated_results = self.get_paginated_response(serializer.data)

        if self.paginator.count > (self.paginator.offset + self.paginator.limit):
            max_current = self.paginator.offset + self.paginator.limit
        else:
            max_current = self.paginator.count
        current_page_results = "%s-%s" % (self.paginator.offset + 1, max_current)

        # fmt: off
        return Response({
            "playbook": playbook.data,
            "hosts": hosts.data,
            "files": files.data,
            "records": records.data,
            "results": paginated_results.data,
            "current_page_results": current_page_results,
            "search_form": search_form
        })
        # fmt: on


class Host(generics.RetrieveAPIView):
    """
    Returns a page for a detailed view of a host
    """

    queryset = models.Host.objects.all()
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "host.html"

    def get(self, request, *args, **kwargs):
        host = self.get_object()
        serializer = serializers.DetailedHostSerializer(host)
        return Response({"host": serializer.data})


class File(generics.RetrieveAPIView):
    """
    Returns a page for a detailed view of a file
    """

    queryset = models.File.objects.all()
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "file.html"

    def get(self, request, *args, **kwargs):
        file = self.get_object()
        serializer = serializers.DetailedFileSerializer(file)
        return Response({"file": serializer.data})


class Result(generics.RetrieveAPIView):
    """
    Returns a page for a detailed view of a result
    """

    queryset = models.Result.objects.all()
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "result.html"

    def get(self, request, *args, **kwargs):
        # Results can contain a wide array of non-ascii or binary characters, escape them
        codecs.register_error("strict", codecs.lookup_error("surrogateescape"))
        result = self.get_object()
        serializer = serializers.DetailedResultSerializer(result)
        return Response({"result": serializer.data})


class Record(generics.RetrieveAPIView):
    """
    Returns a page for a detailed view of a record
    """

    queryset = models.Record.objects.all()
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "record.html"

    def get(self, request, *args, **kwargs):
        record = self.get_object()
        serializer = serializers.DetailedRecordSerializer(record)
        return Response({"record": serializer.data})
