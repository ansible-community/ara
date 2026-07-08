ARA Grafana dashboard
=====================

This explains how the ara Grafana dashboard is built and why. It is meant for
anyone reading or changing the dashboard. The exporter that feeds it has its own
notes in ``contrib/prometheus/README.rst``, including why the graphs live here
rather than in the ara web UI (the short version is that simplicity is a feature,
ara records playbooks, and Prometheus with Grafana monitor them).

.. contents:: Table of Contents
   :local:
   :depth: 2

Audience and the one guiding question
-------------------------------------

The dashboard is for a sysadmin or SRE interested in Ansible metrics.
The ara prometheus exporter isn't really intended to monitor ara itself, it
is to expose it's recorded metrics to Prometheus so they can be used in
alerting and dashboards.

Every panel answers one question: what happened in this window?
How much ran, what failed, where, run by whom, and how long it took.
Two constraints follow.

Range-scoped activity, never raw totals. Every ``ara_*`` gauge is a count of
current database state, so plotting it directly shows a huge, slowly growing
number ("how much is in ara") that nobody watches. The activity panels derive
new records in the window from the change in the gauges instead.

Readable with gaps. Playbooks can run intermittently (cron, CI, etc) and thus
result in quiet time ranges.
Panels have to read cleanly even when the data is mostly zero.

The dashboard is generated: never hand-edit the JSON
----------------------------------------------------

``ara-dashboard.json`` is written by ``_generate_dashboard.py``.

It was somewhat of a pain to develop the generator as the source of truth but
it keeps a couple of dozen panels' worth of repetitive JSON readable, enforces
the conventions below in one place, and makes the dashboard verifiable.

It prevents needing to edit the dashboard by hand or tinkering with thousands
of lines of JSON.

To change the dashboard, edit the generator and run it:

.. code-block:: bash

   python3 contrib/grafana/_generate_dashboard.py

Validate after any change: run ``flake8`` on the generator, confirm the JSON
parses, and run the committed validator:

.. code-block:: bash

   python3 contrib/grafana/_validate_dashboard.py

The validator substitutes the Grafana variables, parses every panel expression
as PromQL, and checks that it references only metrics the exporter actually
emits. That last check has caught real bugs, so keep it in the loop.

Query conventions
-----------------

- **delta() for gauges, increase() for the true counters.** Most ``ara_*``
  series are gauges of current database state. ``increase()`` on a gauge re-adds
  the drops that pruning and expiry cause, as false spikes, so gauges use
  ``delta()``. The true counters (``ara_scrape_errors_total`` and the
  ``ara_recorded_playbooks_by_*_total`` activity counters) only go up, so they
  use ``increase()``. The controller, user and version breakdown panels read
  those counters, which is why they are exact rather than delta-approximate.
- **Per-interval buckets.** Gauge-derived activity series are
  ``clamp_min(delta(metric[$__interval]), 0)`` with a 2 minute minimum step:
  contiguous, non-overlapping buckets, so each new record is counted in exactly
  one bar, and wide enough to always contain at least two scrapes (30s scrape,
  30s exporter refresh) so bars never blank out at short ranges. The
  ``clamp_min(..., 0)`` absorbs prune-induced decreases.
- **Range-scoped stats.** The big numbers sum those per-interval buckets over the
  visible range (``reduceOptions.calcs: ["sum"]``), so the number and its
  sparkline describe the same thing: what happened in the window, and when.
- **Hide inactive series.** Breakdown panels wrap the query with
  ``and on(label) (... over $__range > 0.5)`` so label values with no activity in
  the window (an old Ansible version, the unused ``unknown`` status) drop out of
  the stack and the legend. The cutoff is ``0.5`` rather than ``0`` because
  ``increase()`` and ``delta()`` extrapolate to the window edges and can leave a
  sub-count fraction on an idle label, which would otherwise slip through as a
  Total 0 / Max 0 legend row; a real record contributes about 1. For the one
  high-cardinality label (``hostname``) the filter is additionally wrapped in
  ``topk(10, ...)`` so the panel shows the ten busiest hosts in the window. topk
  membership can wobble slightly at the window edges (it is evaluated per
  timestamp), which is fine for eyeballing.

Known approximations
~~~~~~~~~~~~~~~~~~~~

The activity counters removed the three artifacts that deriving activity from
gauges used to have (window-churn undercount, status-transition double count, and
restart or limit-change spikes). Two smaller things are worth keeping in mind:

- The host panels still derive activity from the ``ara_hosts_by_hostname`` gauge
  with ``clamp_min(delta(...))``, since hosts have no counter. On a saturated
  ``--host-limit`` window their legend totals can be nudged by records aging out,
  and an exporter restart or a limit change can show as one large bar. Read the
  host activity as "approximately what happened" rather than an audited count.
- ``increase()`` cannot see a counter series' first sample, so a label value that
  first appears inside the visible range would be undercounted by one. The
  exporter avoids this by zero-seeding each counter cell when its value is first
  seen (see ``contrib/prometheus/README.rst``), which is what keeps the
  controller, user and version panels consistent with each other.

Presentation conventions
------------------------

- **Activity timeseries are stacked bars** (``drawStyle: bars``,
  ``barAlignment: -1`` so each bar is drawn before its timestamp, matching the
  trailing-window delta). Bars suit intermittent runs: zero-height bars vanish
  and gaps stay empty, where lines would bridge quiet periods into misleading
  diagonals. (Per-point ``>0`` filters on line panels were tried and fragment
  into fake diagonals, which is why bars won.) Bar values display with 0
  decimals: they are counts, and the boundary extrapolation of ``delta()`` and
  ``increase()`` produces fractional values whose precision is meaningless.
- **Live state is a line, not bars.** The ``Playbook activity by status`` panel
  overlays a ``running`` line on a second (right) axis, plotting the
  ``ara_playbooks{status="running"}`` gauge directly, so a playbook that runs for
  a long time stays counted for its whole duration. It sits on its own axis
  because concurrency (tens of runs) is a different scale from the per-interval
  bar counts (a handful of new playbooks). The bars themselves cover terminal
  statuses only, because a delta would register a still-running playbook just
  once, at its start.
- **Merged overview stat boxes.** Each box pairs a total with its failure count
  (and unreachable, for results and hosts) as separate colored lines with their
  own sparklines, so failures are visible at a glance without a separate
  "failures" section. Failed is red, unreachable purple, totals a neutral grey so
  the eye goes to a non-zero red. A stat panel shares one sparkline scale across
  all of its values, so on a box with a large total (tasks, results) the failure
  sparkline is dwarfed and reads flat; the failure *count* is still exact, and the
  failure *trend over time* is on the activity panels below (the red failed bars),
  which is where to read it.
- **Semantic status colors everywhere.** failed red, completed and ok green,
  unreachable purple, expired orange, running and skipped blue, changed yellow,
  ignored brown, unknown grey. A red slice always means the same thing.
- **Legends.** Table legends on breakdown panels sort by Total over the range
  (bucketized activity is 0 between runs, so "Last" is useless). The few line
  panels sort by Last. Breakdown legends are pinned to a fixed pixel width so
  panels sharing a row line up and have equal plot widths; a long label (a
  hostname, a container id) truncates with an ellipsis instead of widening its
  panel. The outcomes donut has no table legend: slices self-label with name and
  percent to save width.

Structure
---------

- **Overview**, one top-to-bottom "what is happening" story: merged stat boxes
  (Playbooks, Tasks, Results, Hosts) and the playbook outcomes donut; playbook
  activity and task activity side by side (stacked status bars, each with its
  live ``running`` line overlaid on a second axis); playbook and task
  duration percentiles side by side, each under its activity panel; result
  outcomes by status on its own full-width row for a finer per-interval view;
  top hosts by changed and by failed or unreachable results (50/50, topk 10).
  The panels are kept short (h=6) so the section stays close to a single
  screen.
- **Activity by controller / user / version**, a 2x2 of stacked-bar breakdowns:
  controller, user, Ansible version, Python version. The version panels are the
  "watch the mix shift during an upgrade" view.
- **Exporter health**, small on purpose: ara reachable, scrape errors, metrics
  age and refresh duration stats, plus a scrape and refresh duration timeseries.
  It exists so an SRE can trust (or distrust) everything above it.

History and design decisions
----------------------------

- **No template variables** (``$controller`` or ``$user`` dropdowns) for now.
  Only the windowed ``*_by_*`` metrics carry those labels, so a dropdown would
  silently not filter the whole-database panels, which is worse than no dropdown.
  Revisit only alongside an exporter label change. A base-URL constant for
  linking back to ara is not a filter, so it does not conflict with this.
- **Header deep-links into ara.** Alongside "Open ara" there are "Failed
  playbooks", "Failed tasks" and "Failed hosts" links that carry the dashboard
  time range through to the matching ara list view (``?status=failed`` with
  ``started_after`` / ``started_before`` for playbooks and tasks; ``failed__gt=0``
  with ``updated_after`` for hosts, since host records carry an updated time
  rather than a start/end and the host list honours only the lower bound). They
  use the hidden ``$ara_server`` variable, so they resolve to whichever ara the
  exporter reads from and are empty when reading from the offline client.
- **Outage shading is an annotation.** The "ara unreachable (shading)" toggle
  shades intervals where ``ara_up == 0`` so an outage does not read as a genuine
  quiet period. Grafana annotation toggles carry no hover tooltip (only the
  header links do), so the explanation lives in the shaded region's hover text
  and the toggle name is kept descriptive.
- **No success-rate stat.** The outcomes donut already shows the composition of
  the same range-scoped population, labeled with percentages.
- **Failed and unreachable hosts share one panel.** Unreachable is a rarer,
  related failure mode, and merging keeps the overview to one row of host panels.
- **Running is a live count, overlaid on the activity panel.** A delta of the
  running gauge showed a playbook once at its start, which read as "we only
  counted it once" for a run that stayed running for an hour. The fix is a live
  ``running`` line, plotted straight from ``ara_playbooks{status="running"}`` on
  a second axis of the ``Playbook activity by status`` panel, so concurrency over
  time sits next to the terminal-status bars without needing its own row. The
  bars now cover completed, failed and expired only. (It started as a separate
  full-width panel and was folded into the activity panel to keep the overview
  compact.)
- The dashboard imports with a data source picker (``__inputs``) and needs only
  core panels (timeseries, stat, piechart) on Grafana 10 or newer.
