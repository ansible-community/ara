ARA Prometheus exporter
=======================

This explains how the ``ara prometheus`` exporter is built and why. It is meant
for anyone reading or changing the exporter and the companion Grafana dashboard.
End-user instructions (how to run it, flags, an example scrape config) live in
``doc/source/prometheus.rst``. The dashboard has its own notes in
``contrib/grafana/README.rst``.

.. contents:: Table of Contents
   :local:
   :depth: 2

Goal and scope
--------------

The exporter lets people monitor their Ansible automation with tools they
already run in production: Prometheus for collection and alerting, Grafana for
dashboards. ara records everything that happens during ``ansible-playbook``
runs, so the exporter surfaces that record as Prometheus metrics. The primary
job is to make failures and unreachable hosts something you can alert on. The
secondary job is to let activity and trends be graphed.

The metrics describe Ansible, not ara. They are about playbooks, tasks, results
and hosts. Monitoring the ara server or its database (request rates, query
latency, table sizes) is out of scope, because the usual web server and database
exporters already do that. The only non-Ansible series are a few exporter health
metrics (``ara_up``, ``ara_metrics_age_seconds`` and friends) that tell you
whether the Ansible numbers can be trusted.

Why an exporter instead of graphs in the ARA UI?
------------------------------------------------

A fair question is why ara does not just draw charts and trends in its own web
interface. That is a deliberate non-goal. Simplicity is a feature in ara: it
records Ansible playbooks and makes that record easy to browse. It is not trying
to become a monitoring, alerting or time-series system. A half-built version of
one inside the UI would do both jobs poorly and grow ara's scope without end.

Prometheus and Grafana already do this well, and they are already deployed in
the environments that need it. They bring retention, PromQL, alert routing
through Alertmanager, and dashboards that can put ara's metrics next to
everything else being monitored (CI, fleet, network). Using the right tool for
the job keeps ara small while giving operators more than built-in graphs could.
This exporter and the dashboard are the bridge between the two.

How it works
------------

A collector with a background-refreshed cache
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The exporter is a ``prometheus_client`` custom collector
(``ara/cli/prometheus.py``). On a background interval (``--refresh-interval``,
default 30s) it queries ara, builds the full metric set and caches it in memory.
The ``collect()`` method, which runs on every scrape, serves that cached set.
Refreshes run one at a time on a single background thread.

This keeps the collection cost off the scrape path. A scrape (or a pair of HA
Prometheus servers, or a curious human) is answered almost instantly and never
triggers queries against ara, so a slow collection cannot exceed Prometheus'
``scrape_timeout`` and concurrent scrapes cannot pile onto ara. Freshness stays
bounded and visible: ``ara_metrics_age_seconds`` reports the age of the served
data, and a failed refresh keeps serving the last good data while setting
``ara_up`` to 0 and bumping ``ara_scrape_errors_total``. Setting
``--refresh-interval 0`` disables the cache and builds on every scrape, which is
fine for small databases.

Caching a current-state snapshot is not the same as replaying history (see the
history section below). Nothing is replayed, and no per-run label combinations
are kept across refreshes, so the runaway-cardinality failure mode stays
structurally impossible.

Two tiers of metrics
~~~~~~~~~~~~~~~~~~~~

**Tier 1: whole-database status counts.** Playbooks, tasks and results per
status, plus the total host record count (``ara_hosts``). Each is one cheap
``COUNT`` query (``?limit=1``, read the paginated ``count`` field), accurate over
the whole dataset and scaling to millions of rows. Every status is always
emitted, including zeros, so the series stay stable to graph and alert on. These
are the numbers to alert on.

**Tier 2: recent-window breakdowns.** Playbooks grouped by ``controller``,
``ansible_version``, ``python_version`` and ``user``, the playbook duration
distribution, and per-hostname host outcome sums. A breakdown has to enumerate
rows, so it is bounded: the playbook breakdowns read the most recent
``--playbook-limit`` playbooks (default 1000) and the per-hostname sums read the
most recently updated ``--host-limit`` host records (default 500, 0 disables). A
bounded window keeps cardinality in check and gives the right semantics for
trends, because old runs age out. That is what makes "how is our Ansible version
mix shifting?" actually move over time, which a whole-database count never would.

The per-hostname breakdown reads the ``hosts`` endpoint (one row per host per
playbook, summed per hostname) rather than ``latesthosts`` (one standing row per
distinct host) on purpose. A standing snapshot never responds to a Grafana time
range: a host that ran once long ago, or was decommissioned, would sit in the
series forever. Sums over recent records only move when hosts actually run, so
Grafana can scope them to the selected range with ``clamp_min(delta(...), 0)``,
consistent with the rest of the dashboard.

Result statuses mirror what ara displays
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ara stores a coarse result status (``ok``, ``failed``, ``skipped``,
``unreachable``, ``unknown``) plus two booleans, and derives the status it
actually displays in ``ListResultSerializer.get_status``: ``ok`` with a change
becomes ``changed``, and ``failed`` with ``ignore_errors`` becomes ``ignored``.
The exporter reproduces that with filtered COUNTs, so ``ara_results{status=...}``
is a clean seven-way partition that matches the UI. This is about correctness,
not cosmetics. Counting only the stored status would fold tolerated failures
(``ignore_errors``) into ``failed``, which inflates failure counts and fires
failure alerts on failures the operator chose to ignore.

Durations
~~~~~~~~~

Playbook and task durations over their windows are gauge histograms
(``_bucket``, ``_gcount``, ``_gsum``) plus an exact ``_max`` gauge each. A
classic counter histogram is avoided on purpose: a collector that re-reads the
same rows every refresh would re-observe them and its ``_count`` and ``_sum``
would balloon without meaning. The gauge histogram lets Grafana compute
quantiles (``histogram_quantile``) and averages (``_gsum / _gcount``) without
the exporter having to pick one statistic in advance. ``_max`` is kept because a
histogram cannot give an exact maximum, and a single very slow run is worth
alerting on. Bucket edges are fixed, because coarse buckets are the enemy of a
useful percentile (``histogram_quantile`` interpolates within a bucket), and
each histogram gets edges matched to its scale: minute-level through the
seconds-to-an-hour range where real playbooks cluster, and sub-minute-dense for
tasks, which mostly finish in seconds. A task is one action run across every
host it targets, so its duration covers the whole fan-out; the per-host slices
are the results, which are an order of magnitude more numerous for little extra
signal and are not measured (a result histogram would follow the same pattern if
a need appears).

Labels and cardinality
~~~~~~~~~~~~~~~~~~~~~~

No per-run identifiers (playbook id, name, path) and no timestamps are ever used
as labels. This was notably a mistake when experimenting with the earlier iterations
of this exporter. Each Tier 2 grouping is its own metric, so cardinality stays additive
(controllers plus versions plus users) rather than multiplicative. The one label
driven by fleet size, ``hostname``, is separately bounded by ``--host-limit``.

Querying activity over time
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every ``ara_*`` series except the counters is a gauge of current database state.
New runs only add rows and pruning or expiry only removes old rows, so the
difference of a gauge over a short window reports new activity. The right
function for a gauge is ``delta()``, not ``increase()``: ``increase()`` treats
any decrease (a prune) as a counter reset and adds it back, which produces false
spikes right after a prune. The dashboard and alerts therefore use ``delta()``
(clamped at 0 where sums matter) for the gauges.

The exception is the true counters. ``ara_scrape_errors_total`` and the
``ara_recorded_playbooks_by_*_total`` activity counters only ever go up, so
``increase()`` and ``rate()`` are correct on them and the breakdown panels use
``increase()``. The next section explains why those activity counters exist.

Activity counters vs windowed gauges
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Two kinds of series come out of the recent-playbook window, and they answer
different questions.

The ``ara_playbooks_by_*`` gauges are a snapshot: how many playbooks are in the
recent window right now, per ``(value, status)``. They are good for the current
shape of activity, most usefully the version mix as an upgrade rolls out, since
old runs age out and the distribution moves.

The ``ara_recorded_playbooks_by_*_total`` counters are a running total per
``(value, status)``, only ever increasing. These are what a dashboard should use
with ``increase()`` or ``rate()`` to plot activity over a range. Deriving
activity from the gauges instead (with ``clamp_min(delta(...))``) is only
approximate: it miscounts on three effects that counters avoid. First, window
churn: when the recent window is saturated, a new playbook entering and an old
one leaving can land on the same ``(value, status)`` series and cancel before
``delta()`` sees them, which undercounts when activity is concentrated in one
label value. Second, status transitions: a playbook is recorded as ``running``
and later becomes terminal, so a per-interval delta counts it under two statuses.
Third, restarts and pruning step the gauges, which ``delta()`` reports as spikes.

The counters avoid all three by tallying each playbook exactly once, when it
first reaches a terminal status (completed, failed, expired, unknown), rather
than by diffing snapshots. The exporter remembers which playbook ids it has
already counted, using the fact that ids are monotonic and a playbook only ever
moves forward from ``running`` to terminal:

- a low-water mark below which every id is known finalized and counted,
- a small set of finalized ids above it, pruned as the low-water mark advances,
  so it holds only the currently-running tail and never grows without bound.

The id is an internal watermark. It is never a metric label, so the counters
carry the same cardinality as the matching gauges: one series per
``(value, status)``.

There is one subtlety worth knowing, because it caused a real disagreement
between the breakdown panels. ``increase()`` cannot observe a series' first
increment: the step from "this series does not exist yet" to its first sample
has no earlier point to diff against. So a Grafana range that contains a series'
birth silently drops that first count. Because every distinct label value is its
own counter series, a dimension with more values born inside the range (several
Python versions, or a controller recorded under more than one name) loses more of
those births than a single-valued one, even though every playbook increments all
four dimensions in lockstep. That is why the by-controller, by-user and
by-version panels could report different totals for the same range. The exporter
fixes it by zero-seeding: as soon as a value is first seen in the window, even
while its only playbook is still running, a counter cell for each terminal status
is created at 0. The later 0 to 1 step is then a normal increment that
``increase()`` counts, and the panels agree. The seeded cells are bounded (values
times terminal statuses per dimension) and the dashboard's ``> 0`` legend filter
hides the ones that stay at 0.

Two edge cases remain, and both are benign in practice. A playbook that
finalizes and then ages out of the ``--playbook-limit`` window before any refresh
observes it as terminal is not counted, so keep ``--playbook-limit`` comfortably
above the number of playbooks that can start within one ``--refresh-interval``.
And, as with any counter served by a stateful exporter, a restart resets the
totals and re-counts whatever is in the window. ``increase()`` and ``rate()``
handle the reset, and the recount is bounded by the window size.

History and design decisions
----------------------------

The tradeoffs below are recorded so they do not get relitigated by accident.

**Cardinality is the failure mode (from the first attempt, PR #483).** An
earlier proof of concept proved the idea and taught two lessons, both called out
by its author. First, it labeled metrics with per-run values (``name``, ``path``,
the playbook id, even an ``updated`` timestamp), so the number of time series
grew with the number of rows in the database and made Prometheus and Grafana
crawl. Tellingly, every dashboard query then collapsed those labels again with
``sum by (...)``, so the granular series were pure overhead. This new implementation
of the exporter keeps cardinality bounded and additive, which is the single most
important constraint on its design. Second, it replayed historical records at
start-up, but Prometheus stamps every sample with the scrape time, so the "history"
all landed at start-up and graphed flat. You cannot backfill Prometheus from an
exporter: it only ever describes current state, and Prometheus provides the time
dimension by scraping repeatedly. That is why the exporter caches a current
snapshot and never replays.

**The cached refresh is a freshness-for-cost trade.** Building the metrics on
every scrape is simplest, but it puts the collection cost (and any slow query
against ara) on the scrape path, where it can trip ``scrape_timeout`` or let
several scrapes stampede ara at once. The background refresh moves that cost off
the scrape path at the price of some staleness, bounded by ``--refresh-interval``
and made visible through ``ara_metrics_age_seconds`` and ``ara_up``. Small
instances that do not care can set ``--refresh-interval 0`` and pay on the scrape
path instead.

**Result statuses are derived to match the UI.** Reproducing ara's ``changed``
and ``ignored`` derivation costs two extra COUNT filters but avoids counting
tolerated (``ignore_errors``) failures as real ones, which would inflate failure
alerts. It is worth the cost.

**Activity counters were added, and then zero-seeded.** The breakdown panels
first derived activity from the windowed gauges with ``clamp_min(delta(...))``,
which undercounts on a saturated window and double-counts across status
transitions. The ``ara_recorded_playbooks_by_*_total`` counters replaced that
with an exact tally, one per playbook at its terminal status. A follow-up made
them consistent across dimensions: because ``increase()`` cannot see a counter
series' first sample, panels for dimensions with more distinct values born inside
the range were reading low. Zero-seeding each cell when its value first appears
fixes that (see the counters section above). The counters are terminal-only by
design, so "how many are running right now" is answered by the live
``ara_playbooks{status="running"}`` gauge instead, which the dashboard now plots
directly rather than inferring from a delta.

**Whole-database host roll-ups were removed.** Earlier versions emitted
``ara_hosts_ok``, ``ara_hosts_changed`` and so on: one gauge per outcome counting
host records with at least one such result. They did not partition ``ara_hosts``,
needed a paragraph to explain, and nothing consumed them. The per-hostname
breakdown already gives the useful per-host outcome numbers, windowed and
range-scopeable, so the roll-ups went away and the dashboard sums the breakdown
instead. Note that these host outcome counts are Ansible's own play-recap
numbers, which can differ slightly from counting results by ara-derived status.

**Deliberate limitations and possible future work.**

- The Tier 2 breakdowns reflect the recent window, not the whole database. This
  is intentional (trends need a window) but worth knowing when reading them.
- Scope matches where PR #483 landed: playbooks, tasks, results and hosts. Plays
  and task-level breakdowns (for example by module or action) were left out to
  keep the first cut focused. A breakdown by module would be useful but needs a
  large task window. We could imagine a more expensive ``--all-metrics``
  argument that would capture more metrics at a cost to cardinality.
- A ``by_label`` breakdown (using ara's user-assigned labels, which are bounded
  and already in the playbook payload) is the natural way to answer "which
  automation is failing?" without the ``name`` or ``path`` cardinality trap. It
  is deferred, not rejected.
- Authentication and TLS for the ``/metrics`` endpoint itself are out of scope:
  put it behind the usual reverse proxy. The exporter does authenticate to a
  remote ara API (``--username`` and ``--password``, or client certificates).
