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

REST_FRAMEWORK = {
    # Use URL-based versioning
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': {'v1'},
}

router = DefaultRouter()
router.register(r'playbooks', views.PlaybookViewSet)
router.register(r'plays', views.PlayViewSet)
router.register(r'tasks', views.TaskViewSet)
router.register(r'hosts', views.HostViewSet)
router.register(r'results', views.ResultViewSet)
router.register(r'records', views.RecordViewSet)
router.register(r'files', views.FileViewSet)
# router.register(r'filecontent', views.FileContentViewSet)

urlpatterns = [
    url(r'^(?P<version>[v1]+)/', include(router.urls)),
]
