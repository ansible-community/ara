#  Copyright (c) 2017 Red Hat, Inc.
#
#  This file is part of ARA: Ansible Run Analysis.
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

from flask import Blueprint
from flask import render_template

from ara.db import models
from ara.utils import fast_count

about = Blueprint('about', __name__)


@about.route('/')
def main():
    """ Returns the about page """
    files = fast_count(models.File.query)
    hosts = fast_count(models.Host.query)
    playbooks = fast_count(models.Playbook.query)
    records = fast_count(models.Record.query)
    tasks = fast_count(models.Task.query)
    results = fast_count(models.Result.query)

    return render_template('about.html',
                           active='about',
                           files=files,
                           hosts=hosts,
                           playbooks=playbooks,
                           records=records,
                           tasks=tasks,
                           results=results)
