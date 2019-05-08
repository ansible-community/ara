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

import pkg_resources
from rest_framework.test import APITestCase


class RootTestCase(APITestCase):
    def test_root_endpoint(self):
        result = self.client.get("/")
        self.assertEqual(set(result.data.keys()), set(["kind", "version", "api"]))
        self.assertEqual(result.data["kind"], "ara")
        self.assertEqual(result.data["version"], pkg_resources.get_distribution("ara").version)
        self.assertTrue(len(result.data["api"]), 1)
        self.assertTrue(result.data["api"][0].endswith("/api/v1/"))
