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

import datetime

from django import template
from django.utils.dateparse import parse_datetime

register = template.Library()


@register.filter(name="format_duration")
def format_duration(duration):
    if duration is not None:
        return duration[:-3]
    return duration


@register.filter(name="format_date")
def format_datetime(datetime):
    return parse_datetime(datetime).strftime("%a, %d %b %Y %H:%M:%S %z")


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
