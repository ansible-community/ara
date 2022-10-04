# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django import forms

from ara.api import models


class PlaybookSearchForm(forms.Form):
    ansible_version = forms.CharField(label="Ansible version", max_length=255, required=False)
    client_version = forms.CharField(label="ara client version", max_length=255, required=False)
    server_version = forms.CharField(label="ara server version", max_length=255, required=False)
    python_version = forms.CharField(label="python version", max_length=255, required=False)
    controller = forms.CharField(label="Playbook controller", max_length=255, required=False)
    user = forms.CharField(label="Playbook user", max_length=255, required=False)
    name = forms.CharField(label="Playbook name", max_length=255, required=False)
    path = forms.CharField(label="Playbook path", max_length=255, required=False)
    status = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple, choices=models.Playbook.STATUS, required=False
    )
    label = forms.CharField(label="Playbook label", max_length=255, required=False)
    started_after = forms.DateField(label="Started after", required=False)
    order = forms.CharField(label="Order", max_length=255, required=False)


class ResultSearchForm(forms.Form):
    host_name = forms.CharField(label="Host name", max_length=255, required=False)
    task_name = forms.CharField(label="Task name", required=False)
    changed = forms.BooleanField(label="Changed", required=False)

    status = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple, choices=models.Result.STATUS, required=False
    )


class HostSearchForm(forms.Form):
    name = forms.CharField(label="Host name", max_length=255, required=False)
    playbook = forms.CharField(label="Playbook id", max_length=10, required=False)
    playbook_name = forms.CharField(label="Playbook name", max_length=255, required=False)
    playbook_path = forms.CharField(label="Playbook path", max_length=255, required=False)
    latest = forms.BooleanField(label="latest", required=False)
    changed__gt = forms.IntegerField(label="changed", required=False)
    failed__gt = forms.IntegerField(label="failed", required=False)
    ok__gt = forms.IntegerField(label="ok", required=False)
    skipped__gt = forms.IntegerField(label="skipped", required=False)
    unreachable__gt = forms.IntegerField(label="unreachable", required=False)


class TaskSearchForm(forms.Form):
    name = forms.CharField(label="Task name", max_length=255, required=False)
    uuid = forms.UUIDField(label="Task uuid", max_length=255, required=False)
    path = forms.CharField(label="Task path", max_length=255, required=False)
    lineno = forms.CharField(label="Task line number", max_length=255, required=False)
    playbook = forms.CharField(label="Playbook id", max_length=10, required=False)
    playbook_name = forms.CharField(label="Playbook name", max_length=255, required=False)
    playbook_path = forms.CharField(label="Playbook path", max_length=255, required=False)
    action = forms.CharField(label="Task action", max_length=255, required=False)
    status = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=models.Task.STATUS, required=False)
    # TODO: tags aren't currently searchable, they're compressed in-database
    # Could stop doing that to provide search capability.
