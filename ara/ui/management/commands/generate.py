import os
import shutil

from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from ara.clients.offline import AraOfflineClient


class Command(BaseCommand):
    help = "Generates a static tree of the web application"
    rendered = 0

    @staticmethod
    def create_dirs(path):
        # create main output dir
        if not os.path.exists(path):
            os.mkdir(path)

        # create subdirs
        dirs = ["playbook", "file", "host", "result", "record"]
        for dir in dirs:
            if not os.path.exists(os.path.join(path, dir)):
                os.mkdir(os.path.join(path, dir))

        # Retrieve static assets (../../static)
        shutil.rmtree(os.path.join(path, "static"), ignore_errors=True)
        ui_path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        shutil.copytree(os.path.join(ui_path, "static"), os.path.join(path, "static"))

    def add_arguments(self, parser):
        parser.add_argument("path", help="Path where the static files will be built in", type=str)

    def render(self, template, destination, **kwargs):
        self.rendered += 1
        with open(destination, "w") as f:
            f.write(render_to_string(template, kwargs))

    def handle(self, *args, **options):
        path = options.get("path")
        self.create_dirs(path)

        client = AraOfflineClient(run_sql_migrations=False)
        playbooks = client.get("/api/v1/playbooks")
        print("[ara] Generating static files for %s playbooks at %s..." % (playbooks["count"], path))

        # Generate index file with summary of playbooks
        destination = os.path.join(path, "index.html")
        data = {"playbooks": playbooks["results"], "static_generation": True, "page": "index"}
        self.render("index.html", destination, **data)

        for playbook in playbooks["results"]:
            # Retrieve additional playbook details
            detailed_playbook = client.get("/api/v1/playbooks/%s" % playbook["id"])

            # Generate playbook report
            destination = os.path.join(path, "playbook/%s.html" % detailed_playbook["id"])
            data = {"playbook": detailed_playbook, "static_generation": True}
            self.render("playbook.html", destination, **data)

            for file in detailed_playbook["files"]:
                # Retrieve file details
                detailed_file = client.get("/api/v1/files/%s" % file["id"])

                # Generate file page
                destination = os.path.join(path, "file/%s.html" % detailed_file["id"])
                data = {"file": detailed_file, "static_generation": True}
                self.render("file.html", destination, **data)

            for host in detailed_playbook["hosts"]:
                # Retrieve host details
                detailed_host = client.get("/api/v1/hosts/%s" % host["id"])

                # Generate host page
                destination = os.path.join(path, "host/%s.html" % detailed_host["id"])
                data = {"host": detailed_host, "static_generation": True}
                self.render("host.html", destination, **data)

            # Results are not at the top level of the playbook object but are instead
            # nested inside tasks which are themselves inside plays.
            # We can query the results endpoint to get the list of results for a playbook.
            results = client.get("/api/v1/results", playbook=detailed_playbook["id"])
            for result in results["results"]:
                # Get result details
                detailed_result = client.get("/api/v1/results/%s" % result["id"])

                # Generate result page
                destination = os.path.join(path, "result/%s.html" % detailed_result["id"])
                data = {"result": detailed_result, "static_generation": True}
                self.render("result.html", destination, **data)

            for record in detailed_playbook["records"]:
                # Retrieve record details
                detailed_record = client.get("/api/v1/records/%s" % record["id"])

                # Generate record page
                destination = os.path.join(path, "record/%s.html" % record["id"])
                data = {"record": detailed_record, "static_generation": True}
                self.render("record.html", destination, **data)

        print("[ara] %s files generated." % self.rendered)
