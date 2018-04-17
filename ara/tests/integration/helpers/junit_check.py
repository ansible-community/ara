#!/usr/bin/env python
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

import unittest
import sys

from lxml import etree


class TestJunitGeneration(unittest.TestCase):

    def setUp(self):
        self.tree = etree.parse(TestJunitGeneration.path)

    def test_testsuites_elem(self):
        testsuites = self.tree.getroot()
        self.assertEqual(testsuites.tag, "testsuites")
        self.assertEqual(testsuites.get("failures"), "2")

    def test_testsuite_elem(self):
        testsuite = self.tree.getroot()[0]
        self.assertEqual(testsuite.tag, "testsuite")
        self.assertEqual(testsuite.get("errors"), "0")
        self.assertEqual(testsuite.get("skipped"), "5")

    def test_skipped_elem(self):
        remove_a_file = self.tree.xpath(
            "//testcase [@name='smoke-tests : Test a skipped task']")[0]
        skipped = remove_a_file[0]
        self.assertEqual(skipped.tag, "skipped")
        self.assertEqual(skipped.get("type"), "skipped")


if __name__ == "__main__":
    TestJunitGeneration.path = sys.argv.pop()
    unittest.main()
