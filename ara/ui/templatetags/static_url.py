# Copyright (c) 2021 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django import template

register = template.Library()


@register.simple_tag(name="static_url", takes_context=True)
def static_url(context, url):
    if not context["static_generation"]:
        return url

    if url.startswith("/"):
        url = url[1:]

    if context["page"] != "index":
        url = "../%s" % url

    return url
