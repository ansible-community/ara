# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django.urls import path
from django.views.generic import TemplateView

from ara.ui import views

app_name = "ui"
urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path("distributed", views.Distributed.as_view(), name="distributed"),
    path("hosts", views.HostIndex.as_view(), name="host_index"),
    path("tasks", views.TaskIndex.as_view(), name="task_index"),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path("playbooks/<int:pk>.html", views.Playbook.as_view(), name="playbook"),
    path("results/<int:pk>.html", views.Result.as_view(), name="result"),
    path("files/<int:pk>.html", views.File.as_view(), name="file"),
    path("hosts/<int:pk>.html", views.Host.as_view(), name="host"),
    path("records/<int:pk>.html", views.Record.as_view(), name="record"),
]
