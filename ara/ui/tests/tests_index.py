# Copyright (c) 2026 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APITestCase

from ara.api.tests import factories


class IndexTestCase(APITestCase):
    """
    The web UI playbook index (ara.ui.views.Index) builds its own queryset, separately
    from the REST API viewset, so it needs its own regression coverage for issue #534.
    """

    @staticmethod
    def _populate_playbook(playbook):
        # file= is passed to TaskFactory so its default file SubFactory does not build a
        # File with its own playbook SubFactory and create a stray playbook, which would
        # skew the query-count assertion below.
        play = factories.PlayFactory(playbook=playbook)
        file_content = factories.FileContentFactory()
        task_file = factories.FileFactory(playbook=playbook, path="/tasks-%s.yml" % playbook.id, content=file_content)
        host = factories.HostFactory(playbook=playbook, name="host-%s" % playbook.id)
        task = factories.TaskFactory(playbook=playbook, play=play, file=task_file)
        factories.ResultFactory(playbook=playbook, play=play, task=task, host=host)
        factories.RecordFactory(playbook=playbook, key="record-%s" % playbook.id)
        playbook.labels.add(factories.LabelFactory(name="label-%s" % playbook.id))
        return playbook

    def test_index_renders(self):
        self._populate_playbook(factories.PlaybookFactory())
        response = self.client.get("/")
        self.assertEqual(200, response.status_code)

    def test_index_has_no_n_plus_one_queries(self):
        # The playbook index must be served in a constant number of queries regardless of
        # how many playbooks it lists; otherwise each extra playbook adds its own
        # per-relationship count queries (the N+1 problem from issue #534).
        self._populate_playbook(factories.PlaybookFactory())
        with CaptureQueriesContext(connection) as one_playbook:
            self.assertEqual(200, self.client.get("/").status_code)

        self._populate_playbook(factories.PlaybookFactory())
        with CaptureQueriesContext(connection) as two_playbooks:
            self.assertEqual(200, self.client.get("/").status_code)

        self.assertEqual(
            len(one_playbook.captured_queries),
            len(two_playbooks.captured_queries),
            "Query count grew with the number of playbooks (N+1 regression):\n%s"
            % "\n".join(query["sql"] for query in two_playbooks.captured_queries),
        )
