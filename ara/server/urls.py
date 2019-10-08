#  Copyright (c) 2019 Red Hat, Inc.
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

import urllib.parse

import pbr.version
from django.contrib import admin
from django.urls import include, path
from rest_framework.response import Response
from rest_framework.views import APIView


# fmt: off
class APIIndex(APIView):
    def get(self, request):
        return Response({
            "kind": "ara",
            "version": pbr.version.VersionInfo("ara").release_string(),
            "api": list(map(lambda x: urllib.parse.urljoin(
                request.build_absolute_uri(), x),
                [
                    "v1/",
                ]))
        })


urlpatterns = [
    path("", include("ara.ui.urls")),
    path("api/", APIIndex.as_view(), name='api-index'),
    path("api/v1/", include("ara.api.urls")),
    path("admin/", admin.site.urls),
    path("healthcheck/", include("health_check.urls")),
]
# fmt: on
