# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django import template

register = template.Library()


@register.simple_tag(name="static_url", takes_context=True)
def static_url(context, url):
    """
    The statically generated version of the website (via `ara-manage generate`) needs to have relative links instead of
    absolute links in order to let it be hosted under any directory, for example http://logserver/some/path/ara-report.
    This filter adapts links from the django URL tag so they are more like "playbooks/<id>.html" and less like
    "/playbooks/<id>.html".
    """
    if not context["static_generation"]:
        return url

    if url.startswith("/"):
        url = url[1:]

    if context["page"] != "index":
        url = "../%s" % url

    return url
