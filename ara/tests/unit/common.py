#  Copyright (c) 2017 Red Hat, Inc.
#
#  This file is part of ARA: Ansible Run Analysis.
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

import unittest
import shutil
import tempfile

from ara.api.client import get_client
import ara.db.models as m
import ara.webapp as w


class TestAra(unittest.TestCase):
    """
    Common setup/teardown for ARA tests
    """
    def setUp(self):
        self.config = {
            'SQLALCHEMY_DATABASE_URI': 'sqlite://',
            'TESTING': True
        }

        self.app = w.create_app(self)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = get_client(client='python')
        self.tmpdir = tempfile.mkdtemp(prefix='ara')

        m.db.create_all()

    def tearDown(self):
        m.db.session.remove()
        m.db.drop_all()
        self.app_context.pop()
        shutil.rmtree(self.tmpdir)
