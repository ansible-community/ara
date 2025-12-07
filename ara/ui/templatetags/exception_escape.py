# Copyright (c) 2025 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django import template

register = template.Library()


@register.filter
def escape_for_exception(value):
    """
    Escape for HTML attribute while preserving line breaks as <br>.
    Shouldn't have been necessary using escape/force_escape/escapejs but
    it seems the behavior isn't the one we want for exception popovers.
    Exceptions can contain a bunch of characters including quotes and single quotes
    so we need to handle them.
    """
    if not value:
        return value
    # Escape HTML entities (order matters - & first)
    value = value.replace("&", "&amp;")
    value = value.replace("<", "&lt;")
    value = value.replace(">", "&gt;")
    value = value.replace('"', "&quot;")
    value = value.replace("'", "&#x27;")
    # Convert newlines to <br>
    value = value.replace("\n", "<br>")
    return value
