import codecs
import os
import shutil

from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from ara.api import models, serializers


class Command(BaseCommand):
    help = "Generates a static tree of the web application"
    rendered = 0

    @staticmethod
    def create_dirs(path):
        # create main output dir
        if not os.path.exists(path):
            os.mkdir(path)

        # create subdirs
        dirs = ["playbooks", "files", "hosts", "results", "records"]
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

        # Index
        destination = os.path.join(path, "index.html")
        data = {"data": {"results": serializer.data}, "static_generation": True, "page": "index"}
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

            # Results are paginated in the dynamic version and the template expects data in a specific format
            formatted_results = {"count": len(results.data), "results": results.data}

            destination = os.path.join(path, "playbooks/%s.html" % playbook.data["id"])
            self.render(
                "playbook.html",
                destination,
                static_generation=True,
                playbook=playbook.data,
                hosts=hosts.data,
                files=files.data,
                records=records.data,
                results=formatted_results,
                current_page_results=None,
                search_form=None,
            )

        # Files
        query = models.File.objects.all()
        for file in query.all():
            destination = os.path.join(path, "files/%s.html" % file.id)
            serializer = serializers.DetailedFileSerializer(file)
            data = {"file": serializer.data, "static_generation": True}
            self.render("file.html", destination, **data)

        # Hosts
        query = models.Host.objects.all()
        for host in query.all():
            destination = os.path.join(path, "hosts/%s.html" % host.id)
            serializer = serializers.DetailedHostSerializer(host)
            data = {"host": serializer.data, "static_generation": True}
            self.render("host.html", destination, **data)

        # Results
        query = models.Result.objects.all()
        for result in query.all():
            destination = os.path.join(path, "results/%s.html" % result.id)
            serializer = serializers.DetailedResultSerializer(result)
            data = {"result": serializer.data, "static_generation": True}
            self.render("result.html", destination, **data)

        # Records
        query = models.Record.objects.all()
        for record in query.all():
            destination = os.path.join(path, "records/%s.html" % record.id)
            serializer = serializers.DetailedRecordSerializer(record)
            data = {"record": serializer.data, "static_generation": True}
            self.render("record.html", destination, **data)

        print("[ara] %s files generated." % self.rendered)
