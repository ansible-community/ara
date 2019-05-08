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
router.register("labels", views.LabelViewSet, base_name="label")
router.register("playbooks", views.PlaybookViewSet, base_name="playbook")
router.register("plays", views.PlayViewSet, base_name="play")
router.register("tasks", views.TaskViewSet, base_name="task")
router.register("hosts", views.HostViewSet, base_name="host")
router.register("results", views.ResultViewSet, base_name="result")
router.register("files", views.FileViewSet, base_name="file")
router.register("records", views.RecordViewSet, base_name="record")

urlpatterns = router.urls
