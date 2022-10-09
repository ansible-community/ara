# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django import template

register = template.Library()


@register.filter(name="strip_db")
def strip_db(path):
    """
    The distributed sqlite backend provides full paths to databases.
    Return the path to the base directory instead.
    """
    return path.replace("/ansible.sqlite", "")
