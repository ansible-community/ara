import os
import shutil

from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from ara.clients.offline import AraOfflineClient


class Command(BaseCommand):
    help = "Generates a static tree of the web application"

    @staticmethod
    def create_dirs(path):
        # create main output dir
        if not os.path.exists(path):
            os.mkdir(path)

        # create subdirs
        dirs = ["playbook", "file", "host", "result"]
        for dir in dirs:
            if not os.path.exists(os.path.join(path, dir)):
                os.mkdir(os.path.join(path, dir))

        # Retrieve static assets (../../static)
        shutil.rmtree(os.path.join(path, "static"), ignore_errors=True)
        ui_path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        shutil.copytree(os.path.join(ui_path, "static"), os.path.join(path, "static"))

    def add_arguments(self, parser):
        parser.add_argument("path", help="Path where the static files will be built in", type=str)

    def handle(self, *args, **options):
        path = options.get("path")
        print("Generating static files at %s..." % path)
        self.create_dirs(path)

        client = AraOfflineClient(run_sql_migrations=False)
        playbooks = client.get("/api/v1/playbooks")

        with open(os.path.join(path, "index.html"), "w") as f:
            f.write(render_to_string("index.html", {"page": "index", "playbooks": playbooks["results"]}))

        for playbook in playbooks["results"]:
            detailed_playbook = client.get("/api/v1/playbooks/%s" % playbook["id"])
            with open(os.path.join(path, "playbook/%s.html" % detailed_playbook["id"]), "w") as f:
                f.write(render_to_string("playbook.html", {"playbook": detailed_playbook}))

            for file in detailed_playbook["files"]:
                detailed_file = client.get("/api/v1/files/%s" % file["id"])
                with open(os.path.join(path, "file/%s.html" % detailed_file["id"]), "w") as f:
                    f.write(render_to_string("file.html", {"file": detailed_file}))

            for host in detailed_playbook["hosts"]:
                detailed_host = client.get("/api/v1/hosts/%s" % host["id"])
                with open(os.path.join(path, "host/%s.html" % detailed_host["id"]), "w") as f:
                    f.write(render_to_string("host.html", {"host": detailed_host}))

            # This is inefficient but the results are currently nested in plays -> tasks -> results
            results = client.get("/api/v1/results", playbook=detailed_playbook["id"])
            for result in results["results"]:
                detailed_result = client.get("/api/v1/results/%s" % result["id"])
                with open(os.path.join(path, "result/%s.html" % detailed_result["id"]), "w") as f:
                    f.write(render_to_string("result.html", {"result": detailed_result}))
