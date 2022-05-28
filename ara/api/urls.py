# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from rest_framework.routers import DefaultRouter

from ara.api import views

router = DefaultRouter(trailing_slash=False)
router.register("labels", views.LabelViewSet, basename="label")
router.register("playbooks", views.PlaybookViewSet, basename="playbook")
router.register("plays", views.PlayViewSet, basename="play")
router.register("tasks", views.TaskViewSet, basename="task")
router.register("hosts", views.HostViewSet, basename="host")
router.register("latesthosts", views.LatestHostViewSet, basename="latesthost")
router.register("results", views.ResultViewSet, basename="result")
router.register("files", views.FileViewSet, basename="file")
router.register("records", views.RecordViewSet, basename="record")

urlpatterns = router.urls
