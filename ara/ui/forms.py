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

from django import forms

from ara.api import models


class PlaybookSearchForm(forms.Form):
    name = forms.CharField(label="Playbook name", max_length=255, required=False)
    path = forms.CharField(label="Playbook path", max_length=255, required=False)
    status = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple, choices=models.Playbook.STATUS, required=False
    )
    label = forms.CharField(label="Playbook label", max_length=255, required=False)
