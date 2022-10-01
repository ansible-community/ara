# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import urllib.parse

from django.contrib import admin
from django.urls import include, path
from rest_framework.response import Response
from rest_framework.views import APIView

from ara.setup import ara_version as ARA_VERSION


# fmt: off
class APIIndex(APIView):
    def get(self, request):
        return Response({
            "kind": "ara",
            "version": ARA_VERSION,
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
