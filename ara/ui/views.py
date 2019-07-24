from django.shortcuts import render

from ara.clients.offline import AraOfflineClient

client = AraOfflineClient(run_sql_migrations=False)


def index(request):
    playbooks = client.get("/api/v1/playbooks")
    return render(request, "index.html", {"page": "index", "playbooks": playbooks["results"]})


def playbook(request, playbook_id):
    playbook = client.get("/api/v1/playbooks/%s" % playbook_id)
    return render(request, "playbook.html", {"playbook": playbook})


def host(request, host_id):
    host = client.get("/api/v1/hosts/%s" % host_id)
    return render(request, "host.html", {"host": host})


def file(request, file_id):
    file = client.get("/api/v1/files/%s" % file_id)
    return render(request, "file.html", {"file": file})


def result(request, result_id):
    result = client.get("/api/v1/results/%s" % result_id)
    return render(request, "result.html", {"result": result})


def record(request, record_id):
    record = client.get("/api/v1/records/%s" % record_id)
    return render(request, "record.html", {"record": record})
