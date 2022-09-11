# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import pkg_resources
from rest_framework.test import APITestCase


class RootTestCase(APITestCase):
    def test_root_endpoint(self):
        result = self.client.get("/api/")
        self.assertEqual(set(result.data.keys()), {"kind", "version", "api"})
        self.assertEqual(result.data["kind"], "ara")
        self.assertEqual(result.data["version"], pkg_resources.get_distribution("ara").version)
        self.assertEqual(len(result.data["api"]), 1)
        self.assertTrue(result.data["api"][0].endswith("/api/v1/"))
