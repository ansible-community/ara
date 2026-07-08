# Copyright (c) 2026 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
import sys
import threading
import time
from datetime import datetime

from cliff.command import Command

from ara.cli.base import global_arguments
from ara.clients.utils import get_client

try:
    from prometheus_client import REGISTRY, start_http_server
    from prometheus_client.core import CounterMetricFamily, GaugeHistogramMetricFamily, GaugeMetricFamily

    HAS_PROMETHEUS_CLIENT = True
except ImportError:
    HAS_PROMETHEUS_CLIENT = False


# The set of statuses each kind of object can have, as defined in ara.api.models.
# We enumerate them explicitly so we can emit a metric for every status (including
# zero values) rather than only the ones that happen to exist at scrape time. This
# keeps the resulting time series stable, which makes them far easier to graph and
# alert on.
PLAYBOOK_STATUSES = ["completed", "failed", "running", "expired", "unknown"]
TASK_STATUSES = ["completed", "failed", "running", "expired", "unknown"]

# The playbook statuses that are terminal: a playbook in one of these is done
# and its status will not change again. "running" is the only non-terminal
# state. The activity counters (ara_recorded_playbooks_by_*) tally a playbook
# once it reaches one of these, so the count reflects the final outcome rather
# than the transient "running" state a playbook is recorded with when it starts.
TERMINAL_PLAYBOOK_STATUSES = frozenset(["completed", "failed", "expired", "unknown"])

# A host record in ara is a per-(host, playbook) row that carries an aggregate
# counter for each of these outcomes. Unlike playbooks/tasks/results, a single
# host row is not "in" one status: it can have a non-zero count for several of
# these at once (e.g. ok=17, changed=1, skipped=1). Keep that in mind when
# reading the host metrics -- see the docstrings below.
HOST_STATUSES = ["ok", "changed", "failed", "skipped", "unreachable"]

# Fixed buckets (in seconds) for the playbook duration histogram. Real Ansible
# playbook runs cluster in the seconds-to-tens-of-minutes range, so the buckets
# are denser there and sparse at the extremes. Coarse buckets are the enemy of a
# useful percentile: histogram_quantile interpolates *linearly within a bucket*,
# so if a whole run of playbooks lands in one wide bucket (e.g. everything
# between 10 and 30 minutes with the old [..., 600, 1800, ...] edges), the p50/
# p95/p99 all get smeared across that bucket's width and can even read higher
# than the true max. The extra edges below give minute-level resolution up to an
# hour, which is where the interesting movement is. The number of buckets is
# still fixed and small, so this adds a constant, bounded number of time series
# regardless of database size. Adjust if your workloads are consistently much
# shorter or longer.
DURATION_BUCKETS = [1, 5, 10, 30, 60, 90, 120, 180, 300, 450, 600, 900, 1200, 1800, 2700, 3600, 5400, 7200]

# Fixed buckets (in seconds) for the task duration histogram. Tasks live on a
# much shorter scale than playbooks: most Ansible tasks finish in under a few
# seconds and the interesting outliers are the tens-of-seconds-to-minutes ones
# (a slow package install, a long-running command across many hosts), so the
# buckets are densest in the sub-minute range and taper off after. Same
# reasoning as DURATION_BUCKETS above: dense buckets where the values live keep
# histogram_quantile's within-bucket interpolation honest, and the bucket count
# stays fixed and small regardless of database size.
TASK_DURATION_BUCKETS = [0.5, 1, 2.5, 5, 10, 15, 30, 60, 120, 300, 600, 1200, 1800, 3600]


def _duration_to_seconds(duration):
    """
    The ara API returns durations as strings formatted like '00:01:23.456789'
    (or '1 day, 0:00:01' for playbooks that run longer than a day). Convert
    that back into a number of seconds we can use as a metric value.

    Returns None when the duration is missing or can't be parsed so the caller
    can decide how to handle it (we simply skip it).

    TODO: It's a bit clunky to parse this, maybe the API should return seconds.
    """
    if not duration:
        return None

    days = 0
    if "," in duration:
        # e.g. "1 day, 0:00:01.123456" or "2 days, 1:02:03"
        day_part, duration = duration.split(",", 1)
        try:
            days = int(day_part.strip().split()[0])
        except (ValueError, IndexError):
            days = 0
        duration = duration.strip()

    try:
        hours, minutes, seconds = duration.split(":")
        return days * 86400 + int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    except (ValueError, AttributeError):
        return None


def _timestamp_to_unix(value):
    """
    Convert an ISO 8601 timestamp as returned by the ara API (e.g.
    '2026-07-03T19:00:06.029467Z') into a unix timestamp in seconds.

    Returns None when the value is missing or unparseable so the caller can skip
    it. The prometheus convention for time metrics is a *_timestamp_seconds gauge
    holding a unix timestamp, which is what this feeds.
    """
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except (ValueError, AttributeError):
        return None


def _duration_histogram(name, documentation, durations, buckets):
    """
    Build a *gauge* histogram (GaugeHistogramMetricFamily) describing the
    distribution of the given durations.

    We use a gauge histogram rather than a classic (counter) histogram on
    purpose. In the scrape-time collector model we re-read the same recent
    playbooks on every refresh, so a cumulative counter histogram would
    re-observe them over and over and its _count/_sum would balloon without
    meaning. A gauge histogram instead represents "the distribution of the
    current window right now", which is exactly what we want and lets Grafana
    compute quantiles with histogram_quantile() (and avg via _gsum/_gcount)
    without the exporter having to pick a single statistic in advance.

    Cardinality is bounded by the number of buckets, so it does not grow with
    the size of the database.
    """
    # Prometheus histogram buckets are cumulative: bucket{le=X} is the number of
    # observations with a value <= X. So each bucket is simply the count at or
    # below its edge (monotonically non-decreasing, ending at +Inf == total).
    counts = [(str(edge), float(sum(1 for d in durations if d <= edge))) for edge in buckets]
    counts.append(("+Inf", float(len(durations))))
    return GaugeHistogramMetricFamily(
        name,
        documentation,
        buckets=counts,
        gsum_value=float(sum(durations)),
    )


class AraCollector(object):
    """
    A prometheus_client custom collector that turns the state of an ara API
    instance into prometheus metrics. See contrib/prometheus/README.rst for the
    full rationale; the short version:

    - **Low cardinality.** No per-run identifiers or timestamps as labels, and
      pre-aggregation rather than one series per row (the mistake an earlier
      experiment made). Breakdowns that need to enumerate label values are
      computed from a bounded recent window, one metric per dimension so
      cardinality stays additive rather than multiplicative.

    - **Cheap scrapes.** By default the collector refreshes from ara on a
      background interval and serves the last built set from an in-memory cache,
      so a scrape never triggers a query against ara and a slow collection can
      never exceed prometheus' scrape_timeout or stampede ara. --refresh-interval
      0 builds fresh on every scrape instead (fine for small databases).

    The metrics come in two tiers: Tier 1 is whole-database status counts
    (playbooks, tasks, results, host total) from cheap COUNT queries, accurate
    over the whole dataset and the numbers to alert on; Tier 2 is bounded
    recent-window breakdowns (playbooks by controller/ansible_version/
    python_version/user as both gauges and monotonic counters, playbook and task
    duration distributions, per-hostname host outcomes) that need to enumerate
    rows.
    """

    def __init__(
        self, client, log, playbook_limit=1000, task_limit=1000, host_limit=500, refresh_interval=30, api_server=None
    ):
        self.client = client
        self.log = log
        self.playbook_limit = playbook_limit
        self.task_limit = task_limit
        self.host_limit = host_limit
        self.refresh_interval = refresh_interval
        # The ara API/web address the exporter was pointed at, when known (the
        # --server URL of the http client). Emitted as a label on ara_api_server
        # so Grafana can build links back into the ara web UI. None for the
        # offline client, which reads a local database with no browsable URL.
        self.api_server = api_server

        # State for the monotonic activity counters (ara_playbooks_recorded_total
        # and friends). Unlike the windowed *_by_* gauges, these only ever go up,
        # so Grafana can use increase()/rate() on them and get exact activity that
        # is immune to window churn, status transitions and pruning. See
        # contrib/prometheus/README.rst for the rationale.
        #
        # We count each playbook exactly once, when it first reaches a terminal
        # status, so the by-status breakdown reflects the outcome rather than the
        # transient "running" state a playbook has when first recorded.
        #   _counter_totals: the accumulated counts, keyed by (label, dimension,
        #     value, status), e.g. ("controller", "forgejo-runner", "completed").
        #   _counted_ids: ids of playbooks already tallied, so we never
        #     double-count one across refreshes.
        #   _counter_low_water: every playbook id at or below this is known to be
        #     finalized (terminal and counted); ids above it may still be running.
        #     Lets us prune _counted_ids without unbounded growth.
        # These persist across refreshes and are guarded by the same lock. The id
        # is an internal watermark only: it is never emitted as a label, so this
        # adds no cardinality over the equivalent *_by_* gauges.
        self._counter_totals = {}
        self._counted_ids = set()
        self._counter_low_water = 0

        # Cache of the last successfully built data metric families, plus the
        # bookkeeping needed to expose freshness/health. Guarded by a lock so a
        # background refresh and concurrent scrapes never trip over each other.
        self._lock = threading.Lock()
        self._families = []
        self._last_refresh = 0.0  # unix ts of the last *successful* refresh
        self._refresh_duration = 0.0  # seconds the last refresh took to build
        self._up = 0  # 1 if the last refresh reached ara, 0 otherwise
        self._refresh_errors = 0  # number of refreshes that failed

    def _count(self, kind, **filters):
        """Return the total number of objects matching the given filters."""
        response = self.client.get("/api/v1/%s" % kind, limit=1, **filters)
        return response["count"]

    # Building the metrics (the expensive part -- one round of ara queries)
    def _build(self):
        """Query ara and return the list of data metric families. Raises on error."""
        collectors = [
            self._collect_playbooks,
            self._collect_tasks,
            self._collect_results,
            self._collect_hosts,
            self._collect_freshness,
            self._collect_playbook_breakdowns,
            self._collect_task_durations,
            self._collect_host_breakdowns,
        ]
        families = []
        for collect in collectors:
            families.extend(collect())
        return families

    def refresh(self):
        """
        Query ara and atomically replace the cached metric families.

        Safe to call from a background thread; never raises. On failure it leaves
        the previous (stale) cache in place, flips ara_up to 0 and bumps the
        error counter so the failure is observable while prometheus keeps getting
        the last good data.
        """
        start = time.time()
        try:
            families = self._build()
        except Exception as e:
            with self._lock:
                self._up = 0
                self._refresh_errors += 1
                self._refresh_duration = time.time() - start
            self.log.error("Failed to collect metrics from ara: %s" % e)
            return

        with self._lock:
            self._families = families
            self._last_refresh = time.time()
            self._refresh_duration = time.time() - start
            self._up = 1

    # Serving the metrics (the inexpensive part, called on every scrape)
    def collect(self):
        """Called by prometheus_client on every scrape of /metrics."""
        serve_start = time.time()

        # In non-cached mode we build synchronously on the scrape path so the
        # metrics are always exactly current. Otherwise we just serve whatever
        # the background refresher last produced.
        if self.refresh_interval == 0:
            self.refresh()

        with self._lock:
            families = list(self._families)
            up = self._up
            last_refresh = self._last_refresh
            refresh_duration = self._refresh_duration
            refresh_errors = self._refresh_errors

        yield from families

        # Exporter health / freshness meta metrics.
        yield GaugeMetricFamily("ara_up", "Whether ara was reachable on the last refresh (1 = up, 0 = down)", value=up)
        yield GaugeMetricFamily(
            "ara_refresh_duration_seconds",
            "Time the last refresh spent querying ara and building metrics",
            value=refresh_duration,
        )
        age = (time.time() - last_refresh) if last_refresh else float("inf")
        yield GaugeMetricFamily(
            "ara_metrics_age_seconds",
            "Age of the metrics currently being served (time since the last successful refresh)",
            value=age,
        )
        yield GaugeMetricFamily(
            "ara_scrape_duration_seconds",
            "Time spent answering this scrape (near-zero when served from cache)",
            value=time.time() - serve_start,
        )
        yield CounterMetricFamily(
            "ara_scrape_errors_total",
            "Total number of refreshes that failed to collect metrics from ara",
            value=refresh_errors,
        )

    def _collect_playbooks(self):
        total = GaugeMetricFamily(
            "ara_playbooks", "Number of playbooks recorded by ara, labeled by status", labels=["status"]
        )
        for status in PLAYBOOK_STATUSES:
            total.add_metric([status], self._count("playbooks", status=status))
        yield total

    def _collect_tasks(self):
        total = GaugeMetricFamily("ara_tasks", "Number of tasks recorded by ara, labeled by status", labels=["status"])
        for status in TASK_STATUSES:
            total.add_metric([status], self._count("tasks", status=status))
        yield total

    def _collect_results(self):
        # Results are the per-task, per-host outcomes. This is the finest grained
        # and most useful signal for failures and unreachable hosts.
        #
        # ara stores a coarse status (ok/failed/skipped/unreachable/unknown) plus
        # two booleans, and *derives* the status it actually displays from them
        # (see ListResultSerializer.get_status):
        #   status=ok    & changed=true        # "changed"
        #   status=failed & ignore_errors=true # "ignored"
        #   otherwise the stored status
        # We reproduce that here so ara_results{status=...} matches what ara shows
        # and forms a clean partition. This matters for correctness, not just
        # cosmetics: counting the stored status alone folds ignored task failures
        # (failed + ignore_errors, which the operator chose to tolerate) into
        # "failed", inflating failure counts and the success-rate denominator, and
        # hides the "changed" vs unchanged-"ok" distinction. Each derived status is
        # a cheap whole-database COUNT with the right filter combination.
        total = GaugeMetricFamily(
            "ara_results",
            "Number of task results recorded by ara, labeled by ara's derived status "
            "(ok/changed/failed/ignored/skipped/unreachable/unknown)",
            labels=["status"],
        )
        # ok, split into truly-ok (unchanged) and changed
        total.add_metric(["ok"], self._count("results", status="ok", changed="false"))
        total.add_metric(["changed"], self._count("results", status="ok", changed="true"))
        # failed, split into real failures and ignored (failed but ignore_errors)
        total.add_metric(["failed"], self._count("results", status="failed", ignore_errors="false"))
        total.add_metric(["ignored"], self._count("results", status="failed", ignore_errors="true"))
        # the remaining stored statuses are not reinterpreted
        for status in ("skipped", "unreachable", "unknown"):
            total.add_metric([status], self._count("results", status=status))
        yield total

    def _collect_hosts(self):
        # A host row is unique per (host, playbook). This whole-database roll-up
        # is the total number of host records, used as the "Hosts" total in the
        # dashboard.
        yield GaugeMetricFamily("ara_hosts", "Number of host records recorded by ara", value=self._count("hosts"))

    def _collect_freshness(self):
        """
        Timestamp metrics for "is automation still running?" and "is a playbook
        stuck?", plus the api_server info metric.

        Both timestamps are cheap: one row each (?limit=1) reading only the
        started field. They are prometheus *_timestamp_seconds gauges (a unix
        timestamp), so alerts compare them against time():
          - no playbook started in 24h:  time() - ara_last_playbook_started... > 86400
          - a playbook stuck running:    time() - ara_running_playbook_oldest... > threshold
        """
        # Most recent playbook by start time, whatever its status.
        latest = self._get_one("playbooks", order="-started")
        started = _timestamp_to_unix(latest["started"]) if latest else None
        if started is not None:
            yield GaugeMetricFamily(
                "ara_last_playbook_started_timestamp_seconds",
                "Unix start time of the most recently started playbook (any status). "
                "Alert on time() minus this to detect that automation has stopped feeding ara.",
                value=started,
            )

        # Oldest still-running playbook: a playbook stuck in "running" (crashed
        # controller, lost callback) never becomes failed, so no failure alert
        # fires. ara's `ara playbook expire` command is the intended cleanup and
        # this metric is a safety net to alert before that runs.
        oldest_running = self._get_one("playbooks", status="running", order="started")
        running_started = _timestamp_to_unix(oldest_running["started"]) if oldest_running else None
        if running_started is not None:
            yield GaugeMetricFamily(
                "ara_running_playbook_oldest_started_timestamp_seconds",
                "Unix start time of the oldest playbook still in the running state. "
                "Alert on time() minus this to catch playbooks stuck running (e.g. a crashed "
                "controller); ara's expire command is the intended cleanup.",
                value=running_started,
            )

        # Info metric: the ara address the exporter is pointed at, in a label, so
        # Grafana can link panels back to the ara web UI. Value is always 1 (the
        # prometheus info-metric convention). Only emitted when known.
        if self.api_server:
            info = GaugeMetricFamily(
                "ara_api_server",
                "The ara API/web server the exporter is reading from, as a label (value is always 1). "
                "Use as a Grafana variable to link back to the ara web UI.",
                labels=["server"],
            )
            info.add_metric([self.api_server], 1)
            yield info

    def _get_one(self, kind, **params):
        """Return the single row matching params (ordered/limited), or None."""
        response = self.client.get("/api/v1/%s" % kind, limit=1, **params)
        results = response.get("results") or []
        return results[0] if results else None

    def _collect_playbook_breakdowns(self):
        """
        Tier 2: from the most recent playbooks, produce two kinds of series
        grouped by controller, ansible_version, python_version and user:

        - Windowed gauges (ara_playbooks_by_*): a snapshot of how many playbooks
          are currently in the window per (value, status). Good for the current
          mix, e.g. watching the ansible_version mix during an upgrade.
        - Monotonic counters (ara_recorded_playbooks_by_*): running totals per
          (value, status) for Grafana to use with increase()/rate(). These are
          exact, unlike delta() on the gauges. See contrib/prometheus/README.rst for why.

        Each grouping is a separate metric so cardinality stays additive rather
        than multiplicative. The counters add no cardinality over the gauges: the
        playbook id used to avoid double-counting is an internal watermark, not a
        label.
        """
        response = self.client.get("/api/v1/playbooks", order="-id", limit=self.playbook_limit)
        playbooks = response["results"]

        yield GaugeMetricFamily(
            "ara_playbooks_window",
            "Number of playbooks considered for the recent-window playbook breakdowns",
            value=len(playbooks),
        )

        # dimension name: metric name, label name, playbook field
        dimensions = [
            ("controller", "ara_playbooks_by_controller", "controller", "controller"),
            ("ansible_version", "ara_playbooks_by_ansible_version", "ansible_version", "ansible_version"),
            ("python_version", "ara_playbooks_by_python_version", "python_version", "python_version"),
            ("user", "ara_playbooks_by_user", "user", "user"),
        ]

        windowed = {dim: {} for dim, _, _, _ in dimensions}
        durations = []
        for playbook in playbooks:
            status = playbook["status"]
            values = {dim: (playbook[field] or "unknown") for dim, _, _, field in dimensions}
            for dim in windowed:
                key = (values[dim], status)
                windowed[dim][key] = windowed[dim].get(key, 0) + 1

            seconds = _duration_to_seconds(playbook["duration"])
            if seconds is not None:
                durations.append(seconds)

        # Fold newly finalized playbooks into the monotonic counters.
        self._update_counters(playbooks, dimensions)

        for dim, metric_name, label_name, _ in dimensions:
            gauge = GaugeMetricFamily(
                metric_name,
                "Number of recent playbooks grouped by %s and status (see ara_playbooks_window)" % label_name,
                labels=[label_name, "status"],
            )
            for (value, status), count in windowed[dim].items():
                gauge.add_metric([value, status], count)
            yield gauge

        # Emit the monotonic counters alongside their gauges. Each dimension is
        # its own counter metric (mirroring the by_* gauge names) so that a single
        # metric name has one consistent label set, as Prometheus expects.
        for dim, gauge_name, label_name, _ in dimensions:
            counter = CounterMetricFamily(
                "ara_recorded_playbooks_by_%s" % label_name,
                "Running total of playbooks recorded by ara, grouped by %s and final status. Monotonic; "
                "use with increase()/rate() for exact activity (immune to the recent-window churn that "
                "makes delta() on %s approximate)." % (label_name, gauge_name),
                labels=[label_name, "status"],
            )
            for (cdim, value, status), count in sorted(self._counter_totals.items()):
                if cdim == dim:
                    counter.add_metric([value, status], count)
            yield counter

        # Duration distribution over the window as a gauge histogram, plus a plain
        # max gauge. The histogram lets Grafana compute avg (via _gsum/_gcount)
        # and quantiles (histogram_quantile) so the exporter does not have to pick
        # one statistic. max is kept because a histogram cannot give an exact max
        # and a single very slow run is worth alerting on.
        yield _duration_histogram(
            "ara_playbook_duration_seconds",
            "Distribution of playbook durations in the recent window (see ara_playbooks_window)",
            durations,
            DURATION_BUCKETS,
        )
        yield GaugeMetricFamily(
            "ara_playbook_duration_seconds_max",
            "Maximum duration of playbooks in the recent window (see ara_playbooks_window)",
            value=max(durations) if durations else 0.0,
        )

    def _update_counters(self, playbooks, dimensions):
        """
        Fold newly finalized playbooks into the monotonic
        ara_recorded_playbooks_by_* counters. See contrib/prometheus/README.rst for the rationale;
        this docstring covers the how.

        A playbook is recorded as "running" when it starts and only later moves
        to a terminal status (completed/failed/expired). We want to count each
        playbook exactly once, under its *final* status, so we only tally a
        playbook once it is terminal, and remember which ids we have already
        tallied so a playbook that stays in the window across many refreshes is
        not counted again.

        Playbook ids are monotonically increasing (a BigAutoField), and a
        playbook only ever moves forward from running to a terminal state, so:
          - any id at or below _counter_low_water is already finalized and
            counted -- skip it without even checking;
          - _counted_ids holds the finalized ids above the low-water mark;
          - once every id up to some point has been counted, we advance the
            low-water mark and drop those ids from _counted_ids, so the set only
            ever holds the currently-running tail rather than growing forever.

        The id is used purely as this internal watermark: it is never emitted as
        a label, so the counters carry exactly the same cardinality as the
        ara_playbooks_by_* gauges. A playbook that finalizes and ages out of the
        --playbook-limit window before any refresh observes it as terminal would
        be missed, so keep --playbook-limit comfortably above the number of
        playbooks that can start within one --refresh-interval.

        Zero-seeding: before counting, we make sure a counter cell exists (at 0)
        for every (dimension, value, terminal status) as soon as its value is
        first seen in the window, even while the only playbook carrying that
        value is still running. This matters because increase()/rate() cannot
        observe a series' first increment: the step from "series does not exist"
        to its first sample has no earlier point to diff against, so a Grafana
        range that contains a series' birth silently drops that first count.
        Seeding the cell to 0 first gives increase() the earlier sample it needs,
        so the first real increment is counted and metrics align together.
        The extra cells are bounded (values x terminal statuses per dimension)
        and the dashboard's ">0" legend filter hides the ones that stay at 0.
        """
        # Ensure every observed (dimension, value) has a zero-valued cell for each
        # terminal status before anything increments it. We do not know a
        # still-running playbook's final status, so we seed all of them.
        for playbook in playbooks:
            for dim, _, _, field in dimensions:
                value = playbook[field] or "unknown"
                for status in TERMINAL_PLAYBOOK_STATUSES:
                    self._counter_totals.setdefault((dim, value, status), 0)

        newly_counted = []
        for playbook in playbooks:
            pk = playbook["id"]
            if pk <= self._counter_low_water or pk in self._counted_ids:
                continue
            if playbook["status"] not in TERMINAL_PLAYBOOK_STATUSES:
                continue  # still running; count it on a later refresh

            status = playbook["status"]
            for dim, _, _, field in dimensions:
                value = playbook[field] or "unknown"
                key = (dim, value, status)
                self._counter_totals[key] = self._counter_totals.get(key, 0) + 1
            self._counted_ids.add(pk)
            newly_counted.append(pk)

        # Advance the low-water mark over the contiguous run of finalized ids at
        # the bottom of the tracked set, pruning them so _counted_ids stays small.
        # We only know an id is finalized-or-older once we have seen it, so the
        # candidate floor is the smallest id present in this window.
        if playbooks:
            window_floor = min(playbook["id"] for playbook in playbooks)
            candidate = max(self._counter_low_water, window_floor - 1)
            while (candidate + 1) in self._counted_ids:
                candidate += 1
            if candidate > self._counter_low_water:
                self._counter_low_water = candidate
                self._counted_ids = {pk for pk in self._counted_ids if pk > candidate}

    def _collect_task_durations(self):
        """
        Tier 2: distribution of task durations over the --task-limit most recent
        tasks, as a gauge histogram (ara_task_duration_seconds) plus an exact max
        gauge, mirroring the playbook duration metrics.

        A task is one action (one module invocation) run across every host it
        targets, so its duration is the wall-clock time for the whole fan-out;
        the per-host slices are the results, which are not measured here: there
        are an order of magnitude more of them for little extra signal. If a
        need appears, a result histogram would follow the same pattern. Tasks
        use their own bucket edges (TASK_DURATION_BUCKETS): most tasks finish in
        seconds, a scale the minute-level playbook buckets would smear into one
        or two buckets and ruin histogram_quantile's interpolation.

        The window is one page of --task-limit tasks ordered by most recent.
        """
        if self.task_limit <= 0:
            return

        response = self.client.get("/api/v1/tasks", order="-id", limit=self.task_limit)
        tasks = response["results"]

        yield GaugeMetricFamily(
            "ara_tasks_window",
            "Number of tasks considered for the recent-window task duration distribution",
            value=len(tasks),
        )

        durations = []
        for task in tasks:
            seconds = _duration_to_seconds(task["duration"])
            if seconds is not None:
                durations.append(seconds)

        yield _duration_histogram(
            "ara_task_duration_seconds",
            "Distribution of task durations in the recent window (see ara_tasks_window)",
            durations,
            TASK_DURATION_BUCKETS,
        )
        yield GaugeMetricFamily(
            "ara_task_duration_seconds_max",
            "Maximum duration of tasks in the recent window (see ara_tasks_window)",
            value=max(durations) if durations else 0.0,
        )

    def _collect_host_breakdowns(self):
        """
        Tier 2: per-hostname outcome counters summed over recent host records,
        emitted as ara_hosts_by_hostname{hostname, status}.

        ara stores one host record per (name, playbook), each with its own ok /
        changed / failed / skipped / unreachable counters. We read the most
        recently *updated* --host-limit records and sum their counters per
        hostname. Summing recent records (rather than reading the latesthosts
        standing snapshot) gives a gauge that only moves when hosts actually run,
        so Grafana can scope it to a time range with clamp_min(delta(...)); see
        contrib/prometheus/README.rst for that choice.

        Like the other windowed gauges this is approximate: as the window slides,
        a hostname's sum can drop when its oldest records fall out, which
        clamp_min(delta()) absorbs. Cardinality is distinct hostnames in the
        window x 5 statuses, bounded by --host-limit.
        """
        if self.host_limit <= 0:
            return

        response = self.client.get("/api/v1/hosts", order="-updated", limit=self.host_limit)
        hosts = response["results"]

        yield GaugeMetricFamily(
            "ara_hosts_window",
            "Number of host records considered for the per-hostname breakdown",
            value=len(hosts),
        )

        # Sum counters per hostname: the same name can appear many times (one row
        # per playbook it ran in), and we want the hostname's total across the
        # window, not a single run.
        by_hostname = {}
        for host in hosts:
            name = host.get("name") or "unknown"
            for status in HOST_STATUSES:
                by_hostname[(name, status)] = by_hostname.get((name, status), 0) + (host.get(status, 0) or 0)

        hostname_metric = GaugeMetricFamily(
            "ara_hosts_by_hostname",
            "Sum of per-host ok/changed/failed/skipped/unreachable counters grouped by hostname over the "
            "most recently updated host records (see ara_hosts_window); scope to a time range in Grafana "
            "with clamp_min(delta(...), 0)",
            labels=["hostname", "status"],
        )
        for (name, status), count in by_hostname.items():
            hostname_metric.add_metric([name, status], count)
        yield hostname_metric


class PrometheusExporter(Command):
    """Exposes a prometheus exporter to provide metrics from an instance of ara"""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser = global_arguments(parser)
        # fmt: off
        parser.add_argument(
            "--playbook-limit",
            help=(
                "Number of recent playbooks to consider for the controller, ansible_version and user "
                "breakdowns (default: 1000). Whole-database status counts are not affected by this limit."
            ),
            default=1000,
            type=int,
        )
        parser.add_argument(
            "--task-limit",
            help=(
                "Number of recent tasks to consider for the task duration distribution (default: 1000). "
                "Whole-database status counts are not affected by this limit; set to 0 to disable the "
                "task duration metrics entirely."
            ),
            default=1000,
            type=int,
        )
        parser.add_argument(
            "--host-limit",
            help=(
                "Number of most-recently-updated host records to sum for the per-hostname breakdown "
                "(default: 1000). Read from the hosts endpoint (one row per host per playbook), ordered by "
                "most recently updated, and summed per hostname -- so the breakdown tracks hosts that ran "
                "recently and can be scoped to a Grafana time range. Cardinality of ara_hosts_by_hostname "
                "is the number of distinct hostnames in this window x 5 statuses; set to 0 to disable the "
                "per-hostname breakdown entirely."
            ),
            default=1000,
            type=int,
        )
        parser.add_argument(
            "--refresh-interval",
            help=(
                "How often (in seconds) to refresh metrics from ara in the background and cache them so "
                "scrapes are answered instantly (default: 30). Set to 0 to build metrics on every scrape "
                "instead (always current, but the collection cost is paid on the scrape path)."
            ),
            default=30,
            type=int,
        )
        parser.add_argument(
            "--prometheus-port",
            help="Port on which the prometheus exporter will listen (default: 8001)",
            default=8001,
            type=int,
        )
        parser.add_argument(
            "--prometheus-address",
            help="Address on which the prometheus exporter will listen (default: 0.0.0.0)",
            # Binding to all interfaces is the sensible default for an exporter that
            # prometheus scrapes from another host. Restrict it with this flag if needed.
            default="0.0.0.0",  # nosec B104
            type=str,
        )
        # fmt: on
        return parser

    def take_action(self, args):
        if not HAS_PROMETHEUS_CLIENT:
            self.log.error(
                "The prometheus_client python package must be installed to run this command, "
                "for example with: pip install ara[prometheus]"
            )
            sys.exit(2)

        verify = False if args.insecure else True
        if args.ssl_ca:
            verify = args.ssl_ca
        client = get_client(
            client=args.client,
            endpoint=args.server,
            timeout=args.timeout,
            username=args.username,
            password=args.password,
            cert=args.ssl_cert,
            key=args.ssl_key,
            verify=verify,
            run_sql_migrations=False,
        )

        # Only the http client points at a reasonable ara web UI; the offline
        # client spawns an ephemeral server in the background on a random port
        # and shouldn't be relied on.
        api_server = args.server if args.client == "http" else None

        collector = AraCollector(
            client=client,
            log=self.log,
            playbook_limit=args.playbook_limit,
            task_limit=args.task_limit,
            host_limit=args.host_limit,
            refresh_interval=args.refresh_interval,
            api_server=api_server,
        )

        # In cached mode, prime the cache once synchronously so the very first
        # scrape has data, then keep it fresh from a background thread. Refreshes
        # run one at a time on this single thread, so an expensive collection can
        # never overlap itself or be triggered by an incoming scrape.
        if args.refresh_interval > 0:
            collector.refresh()

            def _refresh_loop():
                while True:
                    time.sleep(args.refresh_interval)
                    collector.refresh()

            thread = threading.Thread(target=_refresh_loop, name="ara-prometheus-refresh", daemon=True)
            thread.start()

        REGISTRY.register(collector)

        start_http_server(args.prometheus_port, addr=args.prometheus_address)
        self.log.info(
            "ara prometheus exporter listening on http://%s:%s/metrics"
            % (args.prometheus_address, args.prometheus_port)
        )

        # The collector/refresher do all the work; the main thread just needs to
        # stay alive so the HTTP server keeps serving.
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            self.log.info("Shutting down ara prometheus exporter")
