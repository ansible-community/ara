from django.urls import path

from ara.ui import views

app_name = "ui"
urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path("playbook/<int:pk>.html", views.Playbook.as_view(), name="playbook"),
    path("result/<int:pk>.html", views.Result.as_view(), name="result"),
    path("file/<int:pk>.html", views.File.as_view(), name="file"),
    path("host/<int:pk>.html", views.Host.as_view(), name="host"),
    path("record/<int:pk>.html", views.Record.as_view(), name="record"),
]
