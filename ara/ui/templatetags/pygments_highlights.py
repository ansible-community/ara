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

import json

from django import template
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import JsonLexer, YamlLexer
from pygments.lexers.special import TextLexer

register = template.Library()


@register.filter(name="format_yaml")
def format_yaml(code):
    formatter = HtmlFormatter(
        linenos="table", anchorlinenos=True, lineanchors="line", linespans="line", cssclass="codehilite"
    )

    if not code:
        code = ""

    return highlight(code, YamlLexer(stripall=True), formatter)


@register.filter(name="format_data")
def format_data(data):
    formatter = HtmlFormatter(cssclass="codehilite")

    if data is None:
        return data

    if isinstance(data, bool) or isinstance(data, int) or isinstance(data, float):
        return highlight(str(data), TextLexer(), formatter)
    elif isinstance(data, str):
        try:
            data = json.dumps(json.loads(data), indent=4, sort_keys=True)
            lexer = JsonLexer()
        except (ValueError, TypeError):
            lexer = TextLexer()
    elif isinstance(data, dict) or isinstance(data, list):
        data = json.dumps(data, indent=4, sort_keys=True)
        lexer = JsonLexer()
    else:
        lexer = TextLexer()

    lexer.stripall = True
    return highlight(data, lexer, formatter)
