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

import datetime
import six
import ara.models as m

from ara.tests.unit.common import TestAra
from ara.tests.unit.common import ansible_run
from oslo_utils import encodeutils


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

        # TODO: Figure out the difference between py2 and py3
        if six.PY2:
            expected = "{u'key': u'value'}"
        else:
            expected = "{'key': 'value'}"
        self.assertEqual(res, expected)

    def test_from_json_escape(self):
        data = '{"key": "value"}'
        t = self.env.from_string('{{ data | from_json | escape }}')
        res = t.render(data=data)

        # TODO: Figure out the difference between py2 and py3
        if six.PY2:
            expected = "{u&#39;key&#39;: u&#39;value&#39;}"
        else:
            expected = "{&#39;key&#39;: &#39;value&#39;}"

        self.assertEqual(res, expected)

    def test_to_json_safe(self):
        data = {'key': 'value'}
        t = self.env.from_string('{{ data | to_nice_json | safe }}')
        res = t.render(data=data)

        self.assertEqual(res, '{\n    "key": "value"\n}')

    def test_to_json_escape(self):
        data = {'key': 'value'}
        t = self.env.from_string('{{ data | to_nice_json | escape }}')
        res = t.render(data=data)

        self.assertEqual(res, '{\n    &#34;key&#34;: &#34;value&#34;\n}')

    def test_to_json_from_string(self):
        data = '{"key": "value"}'
        t = self.env.from_string('{{ data | to_nice_json | safe }}')
        res = t.render(data=data)

        self.assertEqual(res, '{\n    "key": "value"\n}')

    def test_to_json_from_invalid_string(self):
        # json.dumps does not raise exception on a non-json string,
        # it just returns an unicode string
        data = "definitely not json"
        t = self.env.from_string('{{ data | to_nice_json | safe }}')
        res = t.render(data=data)

        self.assertEqual(res, '"definitely not json"')

    def test_jinja_pygments_formatter_string_simple(self):
        data = "string"
        t = self.env.from_string('{{ data | pygments_formatter | safe }}')
        res = t.render(data=data)

        # This is ugly, sorry
        expected = '''<div class="codehilite"><pre><span></span>string\n</pre></div>\n''' # flake8: noqa
        self.assertEqual(res, expected)

    def test_jinja_pygments_formatter_string_json(self):
        data = '{"one": "value", "two": "value"}'
        t = self.env.from_string('{{ data | pygments_formatter | safe }}')
        res = t.render(data=data)

        # This is ugly, sorry
        if six.PY2:
            expected = '''<div class="codehilite"><pre><span></span><span class="p">{</span>\n    <span class="nt">&quot;one&quot;</span><span class="p">:</span> <span class="s2">&quot;value&quot;</span><span class="p">,</span> \n    <span class="nt">&quot;two&quot;</span><span class="p">:</span> <span class="s2">&quot;value&quot;</span>\n<span class="p">}</span>\n</pre></div>\n''' # flake8: noqa
        else:
            expected = '''<div class="codehilite"><pre><span></span><span class="p">{</span>\n    <span class="nt">&quot;one&quot;</span><span class="p">:</span> <span class="s2">&quot;value&quot;</span><span class="p">,</span>\n    <span class="nt">&quot;two&quot;</span><span class="p">:</span> <span class="s2">&quot;value&quot;</span>\n<span class="p">}</span>\n</pre></div>\n'''  # flake8: noqa
        self.assertEqual(res, expected)

    def test_jinja_pygments_formatter_unicode(self):
        data = u"string"
        t = self.env.from_string('{{ data | pygments_formatter | safe }}')
        res = t.render(data=data)

        # This is ugly, sorry
        expected = '''<div class="codehilite"><pre><span></span>string\n</pre></div>\n''' # flake8: noqa
        self.assertEqual(res, expected)

    def test_jinja_pygments_formatter_list(self):
        data = ['one', 'two']
        t = self.env.from_string('{{ data | pygments_formatter | safe }}')
        res = t.render(data=data)

        # This is ugly, sorry
        if six.PY2:
            expected = '''<div class="codehilite"><pre><span></span><span class="p">[</span>\n    <span class="s2">&quot;one&quot;</span><span class="p">,</span> \n    <span class="s2">&quot;two&quot;</span>\n<span class="p">]</span>\n</pre></div>\n''' # flake8: noqa
        else:
            expected = '''<div class="codehilite"><pre><span></span><span class="p">[</span>\n    <span class="s2">&quot;one&quot;</span><span class="p">,</span>\n    <span class="s2">&quot;two&quot;</span>\n<span class="p">]</span>\n</pre></div>\n'''  # flake8: noqa
        self.assertEqual(res, expected)

    def test_jinja_pygments_formatter_dict(self):
        data = {'one': 'value', 'two': 'value'}
        t = self.env.from_string('{{ data | pygments_formatter | safe }}')
        res = t.render(data=data)

        # This is ugly, sorry
        if six.PY2:
            expected = '''<div class="codehilite"><pre><span></span><span class="p">{</span>\n    <span class="nt">&quot;one&quot;</span><span class="p">:</span> <span class="s2">&quot;value&quot;</span><span class="p">,</span> \n    <span class="nt">&quot;two&quot;</span><span class="p">:</span> <span class="s2">&quot;value&quot;</span>\n<span class="p">}</span>\n</pre></div>\n''' # flake8: noqa
        else:
            expected = '''<div class="codehilite"><pre><span></span><span class="p">{</span>\n    <span class="nt">&quot;one&quot;</span><span class="p">:</span> <span class="s2">&quot;value&quot;</span><span class="p">,</span>\n    <span class="nt">&quot;two&quot;</span><span class="p">:</span> <span class="s2">&quot;value&quot;</span>\n<span class="p">}</span>\n</pre></div>\n'''  # flake8: noqa
        self.assertEqual(res, expected)

    def test_jinja_pygments_formatter_integer(self):
        data = 1
        t = self.env.from_string('{{ data | pygments_formatter | safe }}')
        res = t.render(data=data)

        # This is ugly, sorry
        expected = '''<div class="codehilite"><pre><span></span>1\n</pre></div>\n''' # flake8: noqa
        self.assertEqual(res, expected)

    def test_jinja_pygments_formatter_boolean(self):
        data = True
        t = self.env.from_string('{{ data | pygments_formatter | safe }}')
        res = t.render(data=data)

        # This is ugly, sorry
        expected = '''<div class="codehilite"><pre><span></span>True\n</pre></div>\n''' # flake8: noqa
        self.assertEqual(res, expected)

    def test_jinja_yamlhighlight(self):
        data = """- name: Test thing
    hosts: localhost
    tasks:
      - debug:
          msg: "foo"""
        t = self.env.from_string('{{ data | yamlhighlight | safe }}')
        res = t.render(data=data)

        # This is ugly, sorry
        expected = '''<table class="codehilitetable"><tr><td class="linenos"><div class="linenodiv"><pre><a href="#line-1">1</a>\n<a href="#line-2">2</a>\n<a href="#line-3">3</a>\n<a href="#line-4">4</a>\n<a href="#line-5">5</a></pre></div></td><td class="code"><div class="codehilite"><pre><span></span><span id="line-1"><a name="line-1"></a><span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">Test thing</span>\n</span><span id="line-2"><a name="line-2"></a>    <span class="l l-Scalar l-Scalar-Plain">hosts</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">localhost</span>\n</span><span id="line-3"><a name="line-3"></a>    <span class="l l-Scalar l-Scalar-Plain">tasks</span><span class="p p-Indicator">:</span>\n</span><span id="line-4"><a name="line-4"></a>      <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">debug</span><span class="p p-Indicator">:</span>\n</span><span id="line-5"><a name="line-5"></a>          <span class="l l-Scalar l-Scalar-Plain">msg</span><span class="p p-Indicator">:</span> <span class="s">&quot;foo</span>\n</span></pre></div>\n</td></tr></table>'''  # flake8: noqa
        self.assertEqual(res, expected)

    def test_jinja_fast_count(self):
        ansible_run()
        query = m.Task.query

        normal_count = query.count()

        t = self.env.from_string('{{ query | fast_count }}')
        fast_count = t.render(query=query)

        self.assertEqual(normal_count, int(fast_count))
