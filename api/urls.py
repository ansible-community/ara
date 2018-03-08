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

from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from api import views

router = DefaultRouter()
router.register(r'playbooks', views.PlaybookViewSet, base_name='playbooks')
router.register(r'plays', views.PlayViewSet, base_name='plays')
router.register(r'tasks', views.TaskViewSet, base_name='tasks')
router.register(r'hosts', views.HostViewSet, base_name='hosts')
router.register(r'results', views.ResultViewSet, base_name='results')
router.register(r'records', views.RecordViewSet, base_name='records')
router.register(r'files', views.FileViewSet, base_name='files')

urlpatterns = [
    url(r'^', include(router.urls)),
]
