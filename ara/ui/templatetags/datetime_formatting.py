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

from django import template
from django.utils.dateparse import parse_datetime

register = template.Library()


@register.filter(name="format_duration")
def format_duration(duration):
    hours, remainder = divmod(duration.total_seconds(), 60 * 60)
    minutes, seconds = divmod(remainder, 60)
    return "%d:%02d:%02d" % (int(hours), int(minutes), int(seconds))


@register.filter(name="format_date")
def format_datetime(datetime):
    return parse_datetime(datetime).strftime("%a, %d %b %Y %H:%M:%S %z")
