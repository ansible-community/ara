from django.urls import path

from ara.ui import views

app_name = "ui"
urlpatterns = [
    path("", views.index, name="index"),
    path("playbook/<int:playbook_id>.html", views.playbook, name="playbook"),
    path("result/<int:result_id>.html", views.result, name="result"),
    path("file/<int:file_id>.html", views.file, name="file"),
    path("host/<int:host_id>.html", views.host, name="host"),
    path("record/<int:record_id>.html", views.record, name="record"),
]
