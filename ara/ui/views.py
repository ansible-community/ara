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

        # We need to expand the search card if there is a search query, not considering pagination args
        search_args = [arg for arg in request.GET.keys() if arg not in ["limit", "offset"]]
        expand_search = True if search_args else False

        search_form = forms.PlaybookSearchForm(request.GET)

        # fmt: off
        return Response(dict(
            current_page_results=current_page_results,
            data=response.data,
            expand_search=expand_search,
            page="index",
            search_form=search_form,
            static_generation=False
        ))
        # fmt: on


class HostIndex(generics.RetrieveAPIView):
    """
    Returns the latest playbook result for each host (or all playbook results for every hosts)
    """

    renderer_classes = [TemplateHTMLRenderer]
    pagination_class = LimitOffsetPaginationWithLinks
    template_name = "host_index.html"

    def get(self, request, *args, **kwargs):
        search_form = forms.HostSearchForm(request.GET)

        # Sort by updated by default so we have the most recently updated at the top
        order = "-updated"
        if "order" in request.GET:
            order = request.GET["order"]

        # Default is LatestHost (by not requiring "?latest=true") but accept false to
        # return all hosts
        if "latest" in request.GET and request.GET["latest"] == "false":
            queryset = models.Host.objects.all()
            serializer_type = "DetailedHostSerializer"
            filter_type = "HostFilter"
            # TODO: Is there a cleaner way ? Doing this logic in the template seemed complicated.
            checkbox_status = "checked"
            api_link_url = "host-list"
        else:
            queryset = models.LatestHost.objects.all()
            serializer_type = "DetailedLatestHostSerializer"
            filter_type = "LatestHostFilter"
            checkbox_status = ""
            api_link_url = "latesthost-list"

            # Ordering on LatestHost should be applied to the nested host object
            if order.startswith("-"):
                order = "-host__%s" % order[1:]
            else:
                order = "host__%s" % order

        query = getattr(filters, filter_type)(request.GET, queryset=queryset)
        page = self.paginate_queryset(query.qs.all().order_by(order))
        if page is not None:
            serializer = getattr(serializers, serializer_type)(page, many=True)
        else:
            serializer = getattr(serializers, serializer_type)(query, many=True)
        response = self.get_paginated_response(serializer.data)

        if self.paginator.count > (self.paginator.offset + self.paginator.limit):
            max_current = self.paginator.offset + self.paginator.limit
        else:
            max_current = self.paginator.count
        current_page_results = "%s-%s" % (self.paginator.offset + 1, max_current)

        # We need to expand the search card if there is a search query, not considering pagination args
        search_args = [arg for arg in request.GET.keys() if arg not in ["limit", "offset"]]
        expand_search = True if search_args else False

        # fmt: off
        return Response(dict(
            api_link_url=api_link_url,
            checkbox_status=checkbox_status,
            current_page_results=current_page_results,
            data=response.data,
            expand_search=expand_search,
            page="host_index",
            search_form=search_form,
            static_generation=False,
        ))
        # fmt: on


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
            task = models.Task.objects.get(pk=result["task"])
            result["task"] = serializers.SimpleTaskSerializer(task).data
            host = models.Host.objects.get(pk=result["host"])
            result["host"] = serializers.SimpleHostSerializer(host).data
            if result["delegated_to"]:
                delegated = models.Host.objects.get(pk=result["delegated_to"])
                result["delegated_to"] = serializers.SimpleHostSerializer(delegated).data
        paginated_results = self.get_paginated_response(serializer.data)

        if self.paginator.count > (self.paginator.offset + self.paginator.limit):
            max_current = self.paginator.offset + self.paginator.limit
        else:
            max_current = self.paginator.count
        current_page_results = "%s-%s" % (self.paginator.offset + 1, max_current)

        # We need to expand the search card if there is a search query, not considering pagination args
        search_args = [arg for arg in request.GET.keys() if arg not in ["limit", "offset"]]
        expand_search = True if search_args else False

        search_form = forms.ResultSearchForm(request.GET)

        # fmt: off
        return Response(dict(
            current_page_results=current_page_results,
            expand_search=expand_search,
            files=files.data,
            hosts=hosts.data,
            page="playbook",
            playbook=playbook.data,
            records=records.data,
            results=paginated_results.data,
            search_form=search_form,
            static_generation=False,
        ))
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
        host_serializer = serializers.DetailedHostSerializer(host)

        order = "-started"
        if "order" in request.GET:
            order = request.GET["order"]
        result_queryset = models.Result.objects.filter(host=host_serializer.data["id"]).order_by(order).all()
        result_filter = filters.ResultFilter(request.GET, queryset=result_queryset)

        page = self.paginate_queryset(result_filter.qs)
        if page is not None:
            result_serializer = serializers.ListResultSerializer(page, many=True)
        else:
            result_serializer = serializers.ListResultSerializer(result_filter, many=True)

        for result in result_serializer.data:
            task = models.Task.objects.get(pk=result["task"])
            result["task"] = serializers.SimpleTaskSerializer(task).data
            if result["delegated_to"]:
                delegated = models.Host.objects.get(pk=result["delegated_to"])
                result["delegated_to"] = serializers.SimpleHostSerializer(delegated).data
        paginated_results = self.get_paginated_response(result_serializer.data)

        if self.paginator.count > (self.paginator.offset + self.paginator.limit):
            max_current = self.paginator.offset + self.paginator.limit
        else:
            max_current = self.paginator.count
        current_page_results = "%s-%s" % (self.paginator.offset + 1, max_current)

        # We need to expand the search card if there is a search query, not considering pagination args
        search_args = [arg for arg in request.GET.keys() if arg not in ["limit", "offset"]]
        expand_search = True if search_args else False

        search_form = forms.ResultSearchForm(request.GET)

        # fmt: off
        return Response(dict(
            current_page_results=current_page_results,
            expand_search=expand_search,
            host=host_serializer.data,
            page="host",
            results=paginated_results.data,
            search_form=search_form,
            static_generation=False,
        ))
        # fmt: on


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
        return Response({"file": serializer.data, "static_generation": False, "page": "file"})


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
        return Response({"result": serializer.data, "static_generation": False, "page": "result"})


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
        return Response({"record": serializer.data, "static_generation": False, "page": "result"})
