# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from django import template
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import DiffLexer, JsonLexer, YamlLexer
from pygments.lexers.special import TextLexer

register = template.Library()


@register.filter(name="format_yaml")
def format_yaml(code):
    formatter = HtmlFormatter(
        linenos="table",
        anchorlinenos=True,
        lineanchors="line",
        linespans="line",
        cssclass="table-responsive codehilite",
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
            if data.startswith("---"):
                lexer = DiffLexer()
            else:
                lexer = TextLexer()
    elif isinstance(data, dict) or isinstance(data, list):
        data = json.dumps(data, indent=4, sort_keys=True)
        lexer = JsonLexer()
    else:
        lexer = TextLexer()

    lexer.stripall = True
    return highlight(data, lexer, formatter)
