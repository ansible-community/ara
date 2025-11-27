# Copyright (c) 2025 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django import template

register = template.Library()


@register.filter
def percentage(value, total):
    try:
        result = (float(value) / float(total)) * 100
        # Clamp to valid percentage range
        return max(0, min(100, result))
    except (ValueError, ZeroDivisionError, TypeError):
        return 0


@register.filter
def subtract(value, arg):
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0
