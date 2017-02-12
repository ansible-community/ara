#!/usr/bin/env python

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
            "//testcase [@name='Remove a file if it exists']")[0]
        skipped = remove_a_file[0]
        self.assertEqual(skipped.tag, "skipped")
        self.assertEqual(skipped.get("type"), "skipped")


if __name__ == "__main__":
    TestJunitGeneration.path = sys.argv.pop()
    unittest.main()
