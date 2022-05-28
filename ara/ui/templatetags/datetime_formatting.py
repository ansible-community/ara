# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import datetime

from django import template
from django.utils.dateparse import parse_datetime

register = template.Library()


@register.filter(name="duration_from_seconds")
def duration_from_seconds(seconds):
    return str(datetime.timedelta(seconds=seconds))


@register.filter(name="format_duration")
def format_duration(duration):
    if duration is not None:
        return duration[:-4]
    return duration


@register.filter(name="format_date")
def format_datetime(datetime):
    return parse_datetime(datetime).strftime("%d %b %Y %H:%M:%S %z")


@register.simple_tag(name="past_timestamp")
def past_timestamp(weeks=0, days=0, hours=0, minutes=0, seconds=0):
    """
    Produces a timestamp from the past compatible with the API.
    Used to provide time ranges by templates.
    Expects a dictionary of arguments to timedelta, for example:
        datetime.timedelta(hours=24)
        datetime.timedelta(days=7)
    See: https://docs.python.org/3/library/datetime.html#datetime.timedelta
    """
    delta = dict()
    if weeks:
        delta["weeks"] = weeks
    if days:
        delta["days"] = days
    if hours:
        delta["hours"] = hours
    if minutes:
        delta["minutes"] = minutes
    if seconds:
        delta["seconds"] = seconds

    return (datetime.datetime.now() - datetime.timedelta(**delta)).isoformat()
