#  Copyright (c) 2018 Red Hat, Inc.
#
#  This file is part of ARA Records Ansible.
#
#  ARA is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  ARA is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with ARA.  If not, see <http://www.gnu.org/licenses/>.

from rest_framework.routers import DefaultRouter

from ara.api import views

router = DefaultRouter(trailing_slash=False)
router.register("labels", views.LabelViewSet, basename="label")
router.register("playbooks", views.PlaybookViewSet, basename="playbook")
router.register("plays", views.PlayViewSet, basename="play")
router.register("tasks", views.TaskViewSet, basename="task")
router.register("hosts", views.HostViewSet, basename="host")
router.register("results", views.ResultViewSet, basename="result")
router.register("files", views.FileViewSet, basename="file")
router.register("records", views.RecordViewSet, basename="record")

urlpatterns = router.urls
