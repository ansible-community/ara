#   Copyright 2017 Red Hat, Inc. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

import datetime

from ara.tests.unit.common import TestAra


class TestFilters(TestAra):
    '''Tests for our Jinja2 filters'''
    def setUp(self):
        super(TestFilters, self).setUp()
        self.env = self.app.jinja_env

    def tearDown(self):
        super(TestFilters, self).tearDown()

    def test_pathtruncate_short(self):
        path = '/short/path.yml'
        self.assertTrue(len(path) < self.app.config['ARA_PATH_MAX'])

        t = self.env.from_string('{{ path | pathtruncate }}')
        res = t.render(path=path)
        self.assertEqual(res, path)
        self.assertFalse(res.startswith('...'))
        self.assertEqual(res.count('path.yml'), 1)

    def test_pathtruncate_with_length(self):
        path = '/this/is_definitely/a/very/very/long/path.yml'
        self.assertTrue(len(path) > 20)
        t = self.env.from_string('{{ path | pathtruncate(20) }}')
        res = t.render(path=path)

        self.assertNotEqual(res, path)
        self.assertTrue(res.startswith('...'))
        self.assertEqual(res.count('path.yml'), 1)

    def test_pathtruncate_long(self):
        path = '/this/is_definitely/a/very/very/long/path.yml'
        self.assertTrue(len(path) > self.app.config['ARA_PATH_MAX'])
        t = self.env.from_string('{{ path | pathtruncate }}')
        res = t.render(path=path)

        self.assertNotEqual(res, path)
        self.assertTrue(res.startswith('...'))
        self.assertEqual(res.count('path.yml'), 1)

    def test_datefmt(self):
        datestr = '2016-05-25 14:34:00'
        date = datetime.datetime.strptime(datestr, '%Y-%m-%d %H:%M:%S')
        t = self.env.from_string('{{ date | datefmt }}')
        res = t.render(date=date)

        self.assertEqual(res, datestr)

    def test_datefmt_none(self):
        t = self.env.from_string('{{ date | datefmt }}')
        res = t.render(date=None)

        self.assertEqual(res, 'n/a')

    def test_timefmt(self):
        time = datetime.timedelta(seconds=90061)
        t = self.env.from_string('{{ time | timefmt }}')
        res = t.render(time=time)

        self.assertEqual(res, '1 day, 1:01:01')

    def test_timefmt_none(self):
        t = self.env.from_string('{{ time | timefmt }}')
        res = t.render(time=None)

        self.assertEqual(res, 'n/a')

    def test_from_json(self):
        data = '{"key": "value"}'
        t = self.env.from_string('{{ data | from_json | safe }}')
        res = t.render(data=data)

        self.assertEqual(res, u"{u'key': u'value'}")

    def test_to_json(self):
        data = {'key': 'value'}
        t = self.env.from_string('{{ data | to_nice_json | safe }}')
        res = t.render(data=data)

        self.assertEqual(res,
                         u'{\n    "key": "value"\n}')

    def test_to_json_fails(self):
        data = datetime.datetime.now()
        t = self.env.from_string('{{ data | to_nice_json }}')
        res = t.render(data=data)

        self.assertEqual(res, str(data))

    def test_to_json_from_string(self):
        data = '{"key": "value"}'
        t = self.env.from_string('{{ data | to_nice_json | safe }}')
        res = t.render(data=data)

        self.assertEqual(res,
                         u'{\n    "key": "value"\n}')

    def test_to_json_from_invalid_string(self):
        # json.dumps does not raise exception on a non-json string,
        # it just returns an unicode string
        data = "definitely not json"
        t = self.env.from_string('{{ data | to_nice_json | safe }}')
        res = t.render(data=data)

        self.assertEqual(res, u'"definitely not json"')

    def test_jinja_yamlhighlight(self):
        data = """- name: Test thing
  hosts: localhost
  tasks:
    - debug:
        msg: "foo"""
        t = self.env.from_string('{{ data | yamlhighlight | safe }}')
        res = t.render(data=data)

        # This is ugly, sorry
        expected = '''<table class="codehilitetable"><tr><td class="linenos"><div class="linenodiv"><pre><a href="#line-1">1</a>\n<a href="#line-2">2</a>\n<a href="#line-3">3</a>\n<a href="#line-4">4</a>\n<a href="#line-5">5</a></pre></div></td><td class="code"><div class="codehilite"><pre><span></span><span id="line-1"><a name="line-1"></a><span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">Test thing</span>\n</span><span id="line-2"><a name="line-2"></a>  <span class="l l-Scalar l-Scalar-Plain">hosts</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">localhost</span>\n</span><span id="line-3"><a name="line-3"></a>  <span class="l l-Scalar l-Scalar-Plain">tasks</span><span class="p p-Indicator">:</span>\n</span><span id="line-4"><a name="line-4"></a>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">debug</span><span class="p p-Indicator">:</span>\n</span><span id="line-5"><a name="line-5"></a>        <span class="l l-Scalar l-Scalar-Plain">msg</span><span class="p p-Indicator">:</span> <span class="s">&quot;foo</span>\n</span></pre></div>\n</td></tr></table>''' # flake8: noqa
        self.assertEqual(res, expected)
