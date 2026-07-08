# Copyright (c) 2026 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the ara prometheus exporter's activity counters.

These do not touch a database or the network: they drive AraCollector with a
small fake client that returns a canned playbook listing, so they run wherever
prometheus_client is installed without any ara server setup.

The focus is the ara_recorded_playbooks_by_* counters and their zero-seeding,
which is what keeps the by-controller/user/version breakdown panels consistent
with each other (see contrib/prometheus/README.rst).
"""

import logging
import unittest

from ara.cli.prometheus import HAS_PROMETHEUS_CLIENT, TERMINAL_PLAYBOOK_STATUSES

if HAS_PROMETHEUS_CLIENT:
    from ara.cli.prometheus import AraCollector


class FakeClient(object):
    """A stand-in for the ara http/offline client.

    Only implements the get() calls _collect_playbook_breakdowns and
    _collect_task_durations make. The playbook listing it returns can be swapped
    between refreshes to simulate playbooks starting and later finalizing.
    """

    def __init__(self, playbooks, tasks=None):
        self.playbooks = playbooks
        self.tasks = tasks or []

    def get(self, path, **params):
        if path == "/api/v1/playbooks":
            return {"results": list(self.playbooks)}
        if path == "/api/v1/tasks":
            return {"results": list(self.tasks)}
        raise AssertionError("unexpected client call: %s %r" % (path, params))


def _playbook(pk, status, controller="aio1", user="root", ansible="2.19.6", python="3.12.3"):
    return {
        "id": pk,
        "status": status,
        "controller": controller,
        "ansible_version": ansible,
        "python_version": python,
        "user": user,
        "duration": "0:00:10.000000",
    }


def _counter_totals_by_dim(families):
    """Collect emitted ara_recorded_playbooks_by_* samples into {dim: {(value, status): value}}."""
    dim_for_suffix = {
        "ara_recorded_playbooks_by_controller_total": "controller",
        "ara_recorded_playbooks_by_ansible_version_total": "ansible_version",
        "ara_recorded_playbooks_by_python_version_total": "python_version",
        "ara_recorded_playbooks_by_user_total": "user",
    }
    out = {dim: {} for dim in dim_for_suffix.values()}
    for family in families:
        for sample in family.samples:
            dim = dim_for_suffix.get(sample.name)
            if dim is None:
                continue
            label = sample.labels.get(dim)
            out[dim][(label, sample.labels["status"])] = sample.value
    return out


@unittest.skipUnless(HAS_PROMETHEUS_CLIENT, "prometheus_client is not installed")
class RecordedCounterTestCase(unittest.TestCase):
    def _collector(self, client):
        return AraCollector(client=client, log=logging.getLogger("test"), playbook_limit=1000, host_limit=0)

    def test_dimensions_agree_after_finalizing(self):
        # Two controllers, several python versions, one user, one ansible version,
        # a mix of completed and failed. Every terminal playbook increments all
        # four dimensions once, so their totals must match.
        playbooks = [
            _playbook(1, "completed", controller="aio1", python="3.12.3"),
            _playbook(2, "failed", controller="aio1", python="3.14.4"),
            _playbook(3, "completed", controller="localhost", python="3.12.13"),
            _playbook(4, "completed", controller="aio1", python="3.13.5"),
            _playbook(5, "failed", controller="localhost", python="3.12.3"),
        ]
        collector = self._collector(FakeClient(playbooks))
        families = list(collector._collect_playbook_breakdowns())
        totals = _counter_totals_by_dim(families)

        sums = {dim: sum(cells.values()) for dim, cells in totals.items()}
        self.assertEqual(set(sums.values()), {len(playbooks)}, "counter totals differ across dimensions: %r" % sums)

    def test_running_playbook_is_not_counted_yet(self):
        # A running playbook must not contribute to any counter until it finalizes.
        playbooks = [_playbook(1, "completed"), _playbook(2, "running")]
        collector = self._collector(FakeClient(playbooks))
        totals = _counter_totals_by_dim(list(collector._collect_playbook_breakdowns()))
        self.assertEqual(sum(totals["user"].values()), 1)

    def test_new_value_is_zero_seeded_before_it_finalizes(self):
        # A value seen for the first time while its playbook is still running must
        # already have a zero-valued counter cell, so that when the playbook later
        # finalizes, increase() can observe the 0 -> 1 step. Without this, the
        # first playbook of a value born inside a Grafana range is lost.
        client = FakeClient([_playbook(1, "running", python="3.14.4")])
        collector = self._collector(client)
        totals = _counter_totals_by_dim(list(collector._collect_playbook_breakdowns()))

        for status in TERMINAL_PLAYBOOK_STATUSES:
            self.assertEqual(totals["python_version"].get(("3.14.4", status)), 0)

        # Finalize it: the same value now reads 1 under its terminal status and the
        # cell existed at 0 beforehand, which is the precondition increase() needs.
        client.playbooks = [_playbook(1, "completed", python="3.14.4")]
        totals = _counter_totals_by_dim(list(collector._collect_playbook_breakdowns()))
        self.assertEqual(totals["python_version"].get(("3.14.4", "completed")), 1)

    def test_counted_once_across_refreshes(self):
        # A playbook that stays in the window across refreshes is counted once.
        client = FakeClient([_playbook(1, "completed")])
        collector = self._collector(client)
        for _ in range(3):
            totals = _counter_totals_by_dim(list(collector._collect_playbook_breakdowns()))
        self.assertEqual(sum(totals["controller"].values()), 1)


def _task(pk, duration):
    return {"id": pk, "status": "completed", "duration": duration}


@unittest.skipUnless(HAS_PROMETHEUS_CLIENT, "prometheus_client is not installed")
class TaskDurationTestCase(unittest.TestCase):
    """The recent-window task duration histogram (ara_task_duration_seconds)."""

    def _families(self, tasks, task_limit=1000):
        collector = AraCollector(
            client=FakeClient([], tasks=tasks),
            log=logging.getLogger("test"),
            playbook_limit=1000,
            task_limit=task_limit,
            host_limit=0,
        )
        return {family.name: family for family in collector._collect_task_durations()}

    def test_histogram_buckets_and_max(self):
        # 0.2s and 0.4s land at le=0.5; 3s lands at le=5; 45s lands at le=60. The
        # buckets are cumulative, +Inf carries the total and gsum is the plain sum.
        tasks = [
            _task(1, "0:00:00.200000"),
            _task(2, "0:00:00.400000"),
            _task(3, "0:00:03"),
            _task(4, "0:00:45"),
        ]
        families = self._families(tasks)

        buckets = {
            sample.labels["le"]: sample.value
            for sample in families["ara_task_duration_seconds"].samples
            if sample.name.endswith("_bucket")
        }
        self.assertEqual(buckets["0.5"], 2)
        self.assertEqual(buckets["2.5"], 2)
        self.assertEqual(buckets["5"], 3)
        self.assertEqual(buckets["30"], 3)
        self.assertEqual(buckets["60"], 4)
        self.assertEqual(buckets["+Inf"], 4)

        gsum = [s.value for s in families["ara_task_duration_seconds"].samples if s.name.endswith("_gsum")]
        self.assertAlmostEqual(gsum[0], 0.2 + 0.4 + 3 + 45)

        self.assertEqual(families["ara_task_duration_seconds_max"].samples[0].value, 45)
        self.assertEqual(families["ara_tasks_window"].samples[0].value, 4)

    def test_tasks_without_a_duration_are_skipped(self):
        # A task that is still running (or predates duration tracking) has no
        # duration; it must count toward the window but not the distribution.
        tasks = [_task(1, "0:00:10"), _task(2, None)]
        families = self._families(tasks)

        self.assertEqual(families["ara_tasks_window"].samples[0].value, 2)
        buckets = {
            sample.labels["le"]: sample.value
            for sample in families["ara_task_duration_seconds"].samples
            if sample.name.endswith("_bucket")
        }
        self.assertEqual(buckets["+Inf"], 1)
        self.assertEqual(families["ara_task_duration_seconds_max"].samples[0].value, 10)

    def test_task_limit_zero_disables_the_collector(self):
        # --task-limit 0 must not query ara at all and must emit nothing.
        self.assertEqual(self._families([_task(1, "0:00:10")], task_limit=0), {})


if __name__ == "__main__":
    unittest.main()
