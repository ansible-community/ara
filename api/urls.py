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

from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from api import views

urlpatterns = [
    url(r'^$', views.api_root),
    url(r'^playbooks/$', views.PlaybookList.as_view(), name='playbook-list'),
    url(r'^playbooks/(?P<pk>[0-9]+)/$', views.PlaybookDetail.as_view(), name='playbook-detail'),
    url(r'^plays/$', views.PlayList.as_view(), name='play-list'),
    url(r'^plays/(?P<pk>[0-9]+)/$', views.PlayDetail.as_view(), name='play-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
