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

from rest_framework.test import APITestCase

from ara.api.tests import factories


class FileContentTestCase(APITestCase):
    def test_file_content_factory(self):
        file_content = factories.FileContentFactory(sha1="413a2f16b8689267b7d0c2e10cdd19bf3e54208d")
        self.assertEqual(file_content.sha1, "413a2f16b8689267b7d0c2e10cdd19bf3e54208d")
