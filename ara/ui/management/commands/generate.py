# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import codecs
import os
import shutil

from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from ara.api import models, serializers

# Otherwise provided by ara.server.context_processors for ara/ui/templates/partials/about_modal.html
from ara.setup import ara_version as ARA_VERSION


class Command(BaseCommand):
    help = "Generates a static tree of the web application"
    DEFAULT_PARAMS = dict(static_generation=True, ARA_VERSION=ARA_VERSION)
    rendered = 0

    @staticmethod
    def create_dirs(path):
        # create main output dir
        if not os.path.exists(path):
            os.mkdir(path)

        # create subdirs
        dirs = ["playbooks", "files", "hosts", "results", "records", "tasks"]
        for dir in dirs:
            if not os.path.exists(os.path.join(path, dir)):
                os.mkdir(os.path.join(path, dir))

        # Retrieve static assets (../../static)
        shutil.rmtree(os.path.join(path, "static"), ignore_errors=True)
        ui_path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        shutil.copytree(os.path.join(ui_path, "static"), os.path.join(path, "static"))
        # copy robots.txt from templates to root directory
        shutil.copyfile(os.path.join(ui_path, "templates/robots.txt"), os.path.join(path, "robots.txt"))

    def add_arguments(self, parser):
        parser.add_argument("path", help="Path where the static files will be built in", type=str)

    def render(self, template, destination, **kwargs):
        self.rendered += 1
        with open(destination, "w") as f:
            f.write(render_to_string(template, kwargs))

    def handle(self, *args, **options):
        path = options.get("path")
        self.create_dirs(path)

        # TODO: Leverage ui views directly instead of duplicating logic here
        query = models.Playbook.objects.all().order_by("-id")
        serializer = serializers.ListPlaybookSerializer(query, many=True)

        print("[ara] Generating static files for %s playbooks at %s..." % (query.count(), path))

        # Playbook index
        destination = os.path.join(path, "index.html")
        data = {"data": {"results": serializer.data}, "page": "index", **self.DEFAULT_PARAMS}
        self.render("index.html", destination, **data)

        # Escape surrogates to prevent UnicodeEncodeError exceptions
        codecs.register_error("strict", codecs.lookup_error("surrogateescape"))

        # Playbooks
        for pb in query:
            playbook = serializers.DetailedPlaybookSerializer(pb)
            hosts = serializers.ListHostSerializer(
                models.Host.objects.filter(playbook=playbook.data["id"]).order_by("name").all(), many=True
            )
            files = serializers.ListFileSerializer(
                models.File.objects.filter(playbook=playbook.data["id"]).all(), many=True
            )
            records = serializers.ListRecordSerializer(
                models.Record.objects.filter(playbook=playbook.data["id"]).all(), many=True
            )
            results = serializers.ListResultSerializer(
                models.Result.objects.filter(playbook=playbook.data["id"]).all(), many=True
            )

            # Backfill task and host data into results
            for result in results.data:
                task_id = result["task"]
                result["task"] = serializers.SimpleTaskSerializer(models.Task.objects.get(pk=task_id)).data
                host_id = result["host"]
                result["host"] = serializers.SimpleHostSerializer(models.Host.objects.get(pk=host_id)).data
                if result["delegated_to"]:
                    delegated_to = [models.Host.objects.get(pk=delegated) for delegated in result["delegated_to"]]
                    result["delegated_to"] = serializers.SimpleHostSerializer(delegated_to, many=True).data

            # Results are paginated in the dynamic version and the template expects data in a specific format
            formatted_results = {"count": len(results.data), "results": results.data}

            destination = os.path.join(path, "playbooks/%s.html" % playbook.data["id"])
            self.render(
                "playbook.html",
                destination,
                playbook=playbook.data,
                hosts=hosts.data,
                files=files.data,
                records=records.data,
                results=formatted_results,
                current_page_results=None,
                search_form=None,
                page="playbook",
                **self.DEFAULT_PARAMS
            )

        # Files
        query = models.File.objects.all()
        for file in query.all():
            destination = os.path.join(path, "files/%s.html" % file.id)
            serializer = serializers.DetailedFileSerializer(file)
            data = {"file": serializer.data, "page": "file", **self.DEFAULT_PARAMS}
            self.render("file.html", destination, **data)

        # Hosts
        query = models.Host.objects.all()
        for host in query.all():
            destination = os.path.join(path, "hosts/%s.html" % host.id)
            serializer = serializers.DetailedHostSerializer(host)

            # fmt: off
            host_results = serializers.ListResultSerializer(
                models.Result.objects.filter(host=host.id).all(), many=True
            )
            # fmt: on

            # Backfill task data into results
            for result in host_results.data:
                task_id = result["task"]
                result["task"] = serializers.SimpleTaskSerializer(models.Task.objects.get(pk=task_id)).data

            # Results are paginated in the dynamic version and the template expects data in a specific format
            formatted_results = {"count": len(host_results.data), "results": host_results.data}

            self.render(
                "host.html",
                destination,
                current_page_results=None,
                host=serializer.data,
                page="host",
                results=formatted_results,
                search_form=None,
                **self.DEFAULT_PARAMS
            )

        # Results
        query = models.Result.objects.all()
        for result in query.all():
            destination = os.path.join(path, "results/%s.html" % result.id)
            serializer = serializers.DetailedResultSerializer(result)
            data = {"result": serializer.data, "page": "result", **self.DEFAULT_PARAMS}
            self.render("result.html", destination, **data)

        # Records
        query = models.Record.objects.all()
        for record in query.all():
            destination = os.path.join(path, "records/%s.html" % record.id)
            serializer = serializers.DetailedRecordSerializer(record)
            data = {"record": serializer.data, "page": "record", **self.DEFAULT_PARAMS}
            self.render("record.html", destination, **data)

        # Host index
        # The toggle between latests hosts and all hosts is dynamic with a toggle in the UI
        # Provide all hosts for the static version, we can consider adding a CLI flag if there is a use case for it
        query = models.Host.objects.all().order_by("-updated")
        serializer = serializers.DetailedHostSerializer(query, many=True)

        destination = os.path.join(path, "hosts/index.html")
        data = {"data": {"results": serializer.data}, "page": "host_index", **self.DEFAULT_PARAMS}
        self.render("host_index.html", destination, **data)

        # Task index
        query = models.Task.objects.all().order_by("-updated")
        serializer = serializers.DetailedTaskSerializer(query, many=True)

        destination = os.path.join(path, "tasks/index.html")
        data = {"data": {"results": serializer.data}, "page": "task_index", **self.DEFAULT_PARAMS}
        self.render("task_index.html", destination, **data)

        print("[ara] %s files generated." % self.rendered)
