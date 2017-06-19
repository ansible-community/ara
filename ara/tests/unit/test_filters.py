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
import ara.models as m

from ara.tests.unit.common import TestAra
from ara.tests.unit.common import ansible_run


class TestFilters(TestAra):
    '''Tests for our Jinja2 filters'''
    def setUp(self):
        super(TestFilters, self).setUp()
        self.env = self.app.jinja_env

    def tearDown(self):
        super(TestFilters, self).tearDown()

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

    def test_from_json_safe(self):
        data = '{"key": "value"}'
        t = self.env.from_string('{{ data | from_json | safe }}')
        res = t.render(data=data)

        self.assertEqual(res, u"{u'key': u'value'}")

    def test_from_json_escape(self):
        data = '{"key": "value"}'
        t = self.env.from_string('{{ data | from_json | escape }}')
        res = t.render(data=data)

        self.assertEqual(res, u"{u&#39;key&#39;: u&#39;value&#39;}")

    def test_to_json_safe(self):
        data = {'key': 'value'}
        t = self.env.from_string('{{ data | to_nice_json | safe }}')
        res = t.render(data=data)

        self.assertEqual(res, u'{\n    "key": "value"\n}')

    def test_to_json_escape(self):
        data = {'key': 'value'}
        t = self.env.from_string('{{ data | to_nice_json | escape }}')
        res = t.render(data=data)

        self.assertEqual(res, u'{\n    &#34;key&#34;: &#34;value&#34;\n}')

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
        t = self.env.from_string('{{ data | yamlhighlight | escape }}')
        res = t.render(data=data)

        # This is ugly, sorry
        expected = '''&lt;table class=&#34;codehilitetable&#34;&gt;&lt;tr&gt;&lt;td class=&#34;linenos&#34;&gt;&lt;div class=&#34;linenodiv&#34;&gt;&lt;pre&gt;&lt;a href=&#34;#line-1&#34;&gt;1&lt;/a&gt;\n&lt;a href=&#34;#line-2&#34;&gt;2&lt;/a&gt;\n&lt;a href=&#34;#line-3&#34;&gt;3&lt;/a&gt;\n&lt;a href=&#34;#line-4&#34;&gt;4&lt;/a&gt;\n&lt;a href=&#34;#line-5&#34;&gt;5&lt;/a&gt;&lt;/pre&gt;&lt;/div&gt;&lt;/td&gt;&lt;td class=&#34;code&#34;&gt;&lt;div class=&#34;codehilite&#34;&gt;&lt;pre&gt;&lt;span&gt;&lt;/span&gt;&lt;span id=&#34;line-1&#34;&gt;&lt;a name=&#34;line-1&#34;&gt;&lt;/a&gt;&lt;span class=&#34;p p-Indicator&#34;&gt;-&lt;/span&gt; &lt;span class=&#34;l l-Scalar l-Scalar-Plain&#34;&gt;name&lt;/span&gt;&lt;span class=&#34;p p-Indicator&#34;&gt;:&lt;/span&gt; &lt;span class=&#34;l l-Scalar l-Scalar-Plain&#34;&gt;Test thing&lt;/span&gt;\n&lt;/span&gt;&lt;span id=&#34;line-2&#34;&gt;&lt;a name=&#34;line-2&#34;&gt;&lt;/a&gt;    &lt;span class=&#34;l l-Scalar l-Scalar-Plain&#34;&gt;hosts&lt;/span&gt;&lt;span class=&#34;p p-Indicator&#34;&gt;:&lt;/span&gt; &lt;span class=&#34;l l-Scalar l-Scalar-Plain&#34;&gt;localhost&lt;/span&gt;\n&lt;/span&gt;&lt;span id=&#34;line-3&#34;&gt;&lt;a name=&#34;line-3&#34;&gt;&lt;/a&gt;    &lt;span class=&#34;l l-Scalar l-Scalar-Plain&#34;&gt;tasks&lt;/span&gt;&lt;span class=&#34;p p-Indicator&#34;&gt;:&lt;/span&gt;\n&lt;/span&gt;&lt;span id=&#34;line-4&#34;&gt;&lt;a name=&#34;line-4&#34;&gt;&lt;/a&gt;      &lt;span class=&#34;p p-Indicator&#34;&gt;-&lt;/span&gt; &lt;span class=&#34;l l-Scalar l-Scalar-Plain&#34;&gt;debug&lt;/span&gt;&lt;span class=&#34;p p-Indicator&#34;&gt;:&lt;/span&gt;\n&lt;/span&gt;&lt;span id=&#34;line-5&#34;&gt;&lt;a name=&#34;line-5&#34;&gt;&lt;/a&gt;          &lt;span class=&#34;l l-Scalar l-Scalar-Plain&#34;&gt;msg&lt;/span&gt;&lt;span class=&#34;p p-Indicator&#34;&gt;:&lt;/span&gt; &lt;span class=&#34;s&#34;&gt;&amp;quot;foo&lt;/span&gt;\n&lt;/span&gt;&lt;/pre&gt;&lt;/div&gt;\n&lt;/td&gt;&lt;/tr&gt;&lt;/table&gt;'''  # flake8: noqa
        self.assertEqual(res, expected)

    def test_jinja_fast_count(self):
        ansible_run()
        query = m.Task.query

        normal_count = query.count()

        t = self.env.from_string('{{ query | fast_count }}')
        fast_count = t.render(query=query)

        self.assertEqual(normal_count, int(fast_count))
