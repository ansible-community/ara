from django.urls import path
from django.views.generic import TemplateView

from ara.ui import views

app_name = "ui"
urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path("playbook/<int:pk>.html", views.Playbook.as_view(), name="playbook"),
    path("result/<int:pk>.html", views.Result.as_view(), name="result"),
    path("file/<int:pk>.html", views.File.as_view(), name="file"),
    path("host/<int:pk>.html", views.Host.as_view(), name="host"),
    path("record/<int:pk>.html", views.Record.as_view(), name="record"),
]
