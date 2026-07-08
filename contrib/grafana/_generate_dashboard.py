# Copyright (c) 2026 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#!/usr/bin/env python3
"""Generate contrib/grafana/ara-dashboard.json for the ara prometheus exporter.

This builds a Grafana dashboard against the metrics exposed by 'ara prometheus'.
Keeping the dashboard in a generator keeps it readable and makes it easy to
validate that every query references a metric that actually exists.
"""
import json

DS = {"type": "prometheus", "uid": "${DS_PROMETHEUS}"}
_id = 0

# Semantic colors so a "failed" slice/line is always red, "completed" green, etc.
STATUS_COLORS = {
    "completed": "green", "ok": "green",
    "failed": "red",
    "unreachable": "purple",
    "expired": "orange",
    "running": "blue",
    "skipped": "#5794F2",
    "changed": "#FADE2A",
    "ignored": "#C0844D",
    "unknown": "#8e8e8e",
}


def nid():
    global _id
    _id += 1
    return _id


def status_overrides(names):
    """Field overrides pinning each status series to its semantic color."""
    overrides = []
    for name in names:
        color = STATUS_COLORS.get(name)
        if not color:
            continue
        overrides.append({
            "matcher": {"id": "byName", "options": name},
            "properties": [{"id": "color", "value": {"mode": "fixed", "fixedColor": color}}],
        })
    return overrides


def running_overlay_override():
    """Field overrides that draw the 'running' series as a line on a second
    (right) axis, overlaid on the activity bars.

    'running' is the live ara_playbooks{status="running"} gauge, a concurrency
    count, not a per-interval delta like the bars around it. It sits on a
    different scale (tens of concurrent runs versus a handful of new playbooks
    per bar), so it gets its own right axis and is drawn as a light-filled line
    rather than stacked into the bars. The colour still comes from
    status_overrides (blue).
    """
    return [{
        "matcher": {"id": "byName", "options": "running"},
        "properties": [
            {"id": "custom.drawStyle", "value": "line"},
            {"id": "custom.lineWidth", "value": 2},
            {"id": "custom.fillOpacity", "value": 12},
            {"id": "custom.spanNulls", "value": True},
            {"id": "custom.stacking", "value": {"mode": "none", "group": "A"}},
            {"id": "custom.axisPlacement", "value": "right"},
            {"id": "custom.axisLabel", "value": "running (live)"},
        ],
    }]


def target(expr, legend=None, instant=False, ref="A", min_step=None):
    t = {
        "datasource": DS,
        "editorMode": "code",
        "expr": expr,
        "refId": ref,
        "range": not instant,
        "instant": instant,
    }
    if legend is not None:
        t["legendFormat"] = legend
    if min_step is not None:
        # Lower bound on the query step. With delta(...[$__interval]) this keeps
        # the bucket wide enough to always contain >= 2 scrapes (30s scrape,
        # 60s exporter refresh), so bars never blank out at short time ranges.
        t["interval"] = min_step
    return t


def base_fieldconfig(unit=None, decimals=None, color_mode="palette-classic", overrides=None):
    defaults = {
        "color": {"mode": color_mode},
        "mappings": [],
        "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}]},
    }
    if unit:
        defaults["unit"] = unit
    if decimals is not None:
        defaults["decimals"] = decimals
    return {"defaults": defaults, "overrides": overrides or []}


def row(title, y):
    return {
        "type": "row",
        "id": nid(),
        "title": title,
        "collapsed": False,
        "gridPos": {"h": 1, "w": 24, "x": 0, "y": y},
        "panels": [],
    }


def stat(title, expr, gridpos, unit=None, thresholds=None, description="", legend=None,
         instant=True, color_mode=None, calc="lastNotNull", decimals=None, graph_mode="area",
         mappings=None):
    """A single-value stat with a sparkline.

    Used here for the exporter-health values (ara reachable, metrics age, ...),
    which are instantaneous readings. The range-scoped overview counts use
    multistat() instead. `mappings` is a list of Grafana value mappings (e.g.
    render ara_up 1/0 as UP/DOWN).
    """
    fc = base_fieldconfig(unit=unit, decimals=decimals)
    if mappings:
        fc["defaults"]["mappings"] = mappings
    if thresholds:
        fc["defaults"]["thresholds"] = {"mode": "absolute", "steps": thresholds}
        fc["defaults"]["color"] = {"mode": "thresholds"}
    if color_mode:
        fc["defaults"]["color"] = {"mode": color_mode}
    return {
        "type": "stat",
        "id": nid(),
        "title": title,
        "description": description,
        "datasource": DS,
        "gridPos": gridpos,
        "fieldConfig": fc,
        "options": {
            "reduceOptions": {"calcs": [calc], "fields": "", "values": False},
            "orientation": "auto",
            "textMode": "auto",
            "colorMode": "value",
            "graphMode": graph_mode,
            "justifyMode": "auto",
        },
        "targets": [target(expr, legend=legend, instant=instant)],
    }


def timeseries(title, targets, gridpos, unit=None, stack=False, description="", fill=10,
               legend_table=False, overrides=None, span_nulls=True, bars=False):
    """A timeseries panel; lines by default, Kibana-style stacked bars with bars=True.

    Bars are the right shape for the delta-derived activity queries: each bucket
    is a discrete "how many new records landed here", zero-height bars vanish,
    and gaps between runs stay visually empty instead of being bridged by lines.
    barAlignment=-1 draws each bar *before* its timestamp, matching the
    delta-over-trailing-window semantics of the query. Bar values display with 0
    decimals: they are counts, and delta()'s boundary extrapolation produces
    fractional values (6.67 playbooks) whose precision is meaningless anyway.
    """
    custom = {
        "drawStyle": "bars" if bars else "line",
        "lineInterpolation": "linear",
        "lineWidth": 1,
        "fillOpacity": 100 if bars else fill,
        "gradientMode": "none",
        "spanNulls": False if bars else span_nulls,
        "showPoints": "never",
        "pointSize": 5,
        "barAlignment": -1,
        "stacking": {"mode": "normal" if stack else "none", "group": "A"},
        "axisPlacement": "auto",
        "axisLabel": "",
        "scaleDistribution": {"type": "linear"},
    }
    fc = base_fieldconfig(unit=unit, overrides=overrides, decimals=0 if bars else None)
    fc["defaults"]["custom"] = custom
    legend_opts = {"displayMode": "list", "placement": "bottom", "calcs": [], "showLegend": True}
    if legend_table:
        if bars:
            # Bucketized activity is zero between runs, so the "Last" value is
            # almost always 0 and useless to sort by. Sort by the total over the
            # visible range instead: "who did the most in this window".
            calcs, sort_by = ["sum", "max"], "Total"
        else:
            calcs, sort_by = ["lastNotNull", "max"], "Last *"
        legend_opts = {
            "displayMode": "table",
            "placement": "right",
            "calcs": calcs,
            "showLegend": True,
            "sortBy": sort_by,
            "sortDesc": True,
            # Fix the legend width so every breakdown panel has the same plot
            # width (they otherwise size to their longest label, which makes
            # panels in the same row slightly different widths and awkward to
            # compare). Long labels (a hostname, a container id) truncate with an
            # ellipsis rather than widening the column.
            "width": LEGEND_WIDTH,
        }
    return {
        "type": "timeseries",
        "id": nid(),
        "title": title,
        "description": description,
        "datasource": DS,
        "gridPos": gridpos,
        "fieldConfig": fc,
        "options": {"legend": legend_opts, "tooltip": {"mode": "multi", "sort": "desc"}},
        "targets": targets,
    }


def piechart(title, expr, legend, gridpos, description="", overrides=None,
             show_legend=True, display_labels=None):
    legend_opts = {
        "displayMode": "table",
        "placement": "right",
        "showLegend": show_legend,
        "values": ["value", "percent"],
    }
    return {
        "type": "piechart",
        "id": nid(),
        "title": title,
        "description": description,
        "datasource": DS,
        "gridPos": gridpos,
        "fieldConfig": base_fieldconfig(overrides=overrides),
        "options": {
            "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
            "pieType": "donut",
            "displayLabels": display_labels or ["percent"],
            "tooltip": {"mode": "single", "sort": "none"},
            "legend": legend_opts,
        },
        "targets": [target(expr, legend=legend, instant=True)],
    }


# Handy sub-expressions. delta() clamped at 0 = new records of a gauge over a
# window, ignoring the decreases that pruning/expiry cause. Using $__interval
# (the query step) as the window makes the buckets contiguous and
# non-overlapping, so each new record is counted in exactly one bar; the old
# $__rate_interval variant smeared a single event across several overlapping
# samples, which lines rendered as a plateau but bars would double-count
# visually. Pair with target(min_step=BUCKET_MIN_STEP).
BUCKET_MIN_STEP = "2m"  # >= 4x the 30s scrape interval and 2x the 60s refresh

# Fixed pixel width for the right-hand table legends on the breakdown panels, so
# panels sharing a row line up and long labels truncate instead of stealing plot
# width. Wide enough for the Name / Total / Max columns with a readable name.
LEGEND_WIDTH = 240

# Fixed font sizes (px) for the merged overview stat boxes. Grafana otherwise
# auto-fits each value to its cell, so a 3-digit total and a 5-digit total in
# adjacent boxes render at visibly different sizes. Pinning both the title
# (total / failed / unreachable) and the value size makes every overview box
# match. Kept conservative so long labels ("unreachable") and multi-digit counts
# fit their ~2-grid-column cells without clipping.
OVERVIEW_TITLE_SIZE = 16
OVERVIEW_VALUE_SIZE = 30


def new_per_bucket(metric):
    return "clamp_min(delta(%s[$__interval]), 0)" % metric


def active_new_by(label, metric, top=None):
    """Per-interval new-record breakdown by `label`, dropping inactive labels.

    sum by (label) of the per-interval delta gives one series per label value
    that exists in the gauge (including values with no new playbooks in the
    visible range), which show up as all-zero series and clutter the table legend
    (every one reads Total 0 / Max 0). The `and on(label) (... over $__range >
    0.5)` filter keeps only labels whose total over the whole range is a real
    record or more, so the legend lists just the controllers / users / versions
    that actually ran in the window. The cutoff is 0.5 rather than 0 because
    delta()/increase() extrapolate to the window edges and can leave a sub-count
    fraction on an otherwise-idle label; a genuine record contributes about 1.

    For a low-cardinality label (controller, user, version) that is all that is
    needed. For a label that can explode -- hostname, up to --host-limit distinct
    values -- pass top=N to also cap the breakdown to the N busiest labels by
    range total, via topk() in the filter, so the stack and legend stay readable.
    The topk is evaluated over $__range, so membership is by the busiest labels in
    the selected window; it can wobble slightly at the window edges (topk in a
    range query is per-timestamp), which is fine for eyeballing.
    """
    per_interval = "sum by (%s) (%s)" % (label, new_per_bucket(metric))
    in_range = "sum by (%s) (clamp_min(delta(%s[$__range]), 0))" % (label, metric)
    if top is not None:
        keep = "topk(%d, %s) > 0.5" % (top, in_range)
    else:
        keep = "%s > 0.5" % in_range
    return "%s and on(%s) (%s)" % (per_interval, label, keep)


def active_recorded_by(label, counter):
    """Per-interval activity breakdown by `label` from a monotonic counter.

    Same shape and inactive-label filtering as active_new_by, but reads a
    ara_recorded_*_total counter with increase() instead of clamp_min(delta())
    on a gauge. This is exact: it does not undercount when the recent window is
    saturated and one label value dominates (see contrib/prometheus/README.rst).
    Used for the controller/user/version breakdowns, which have counters; the
    per-hostname panels keep active_new_by since hosts have no counter.

    The keep filter uses `> 0.5`, not `> 0`: increase() extrapolates to the
    window edges, so a label value with no real record in the range can still
    carry a sub-count fraction there and slip past `> 0`, showing up as a Total
    0 / Max 0 legend row. A genuine record contributes about 1, so 0.5 is a clean
    cutoff between "had activity" and "extrapolation noise".
    """
    per_interval = "sum by (%s) (increase(%s[$__interval]))" % (label, counter)
    in_range = "sum by (%s) (increase(%s[$__range]))" % (label, counter)
    return "%s and on(%s) (%s > 0.5)" % (per_interval, label, in_range)


def multistat(title, series, gridpos, description=""):
    """A stat panel showing several range-scoped counts, each with a sparkline.

    Used to merge an overview total with its failure counterpart(s) into one box
    (e.g. Playbooks: total + failed) for more information in less space. Each entry
    in `series` is (name, selector, color), where selector is a bare metric
    selector like 'ara_playbooks' or 'ara_playbooks{status="failed"}'.

    Each line plots the *per-interval new records* (sum of clamp_min(delta(...)))
    and reduces with `sum`, so the big number is the total that appeared in the
    range and the sparkline behind it shows *when* they appeared: the same
    activity shape as the bar panels below. (Reducing the raw cumulative gauge
    with `delta` gave the right number but a flat sparkline, because the plotted
    series was then the absolute total, a huge slowly-moving value.) 'failed'
    reads red and 'unreachable' purple via field override; the neutral total
    stays grey. Font sizes are pinned (OVERVIEW_*_SIZE) so every box matches.

    Layout: textMode value_and_name + wideLayout puts each value's name and number
    side by side on one line, which leaves vertical room for Grafana to draw the
    area sparkline behind each value (a stat panel hides the sparkline when a cell
    gets too short -- stacking name above value is what squeezes it out).
    """
    targets = []
    overrides = []
    for i, (name, selector, color) in enumerate(series):
        ref = chr(ord("A") + i)
        expr = "sum(%s)" % new_per_bucket(selector)
        targets.append(target(expr, legend=name, instant=False, ref=ref, min_step=BUCKET_MIN_STEP))
        overrides.append({
            "matcher": {"id": "byFrameRefID", "options": ref},
            "properties": [
                {"id": "displayName", "value": name},
                {"id": "color", "value": {"mode": "fixed", "fixedColor": color}},
            ],
        })
    fc = base_fieldconfig(decimals=0, overrides=overrides)
    fc["defaults"]["color"] = {"mode": "fixed", "fixedColor": "text"}
    return {
        "type": "stat",
        "id": nid(),
        "title": title,
        "description": description,
        "datasource": DS,
        "gridPos": gridpos,
        "fieldConfig": fc,
        "options": {
            "reduceOptions": {"calcs": ["sum"], "fields": "", "values": False},
            "orientation": "vertical",
            "textMode": "value_and_name",
            "wideLayout": True,
            "colorMode": "value",
            "graphMode": "area",
            "justifyMode": "auto",
            # Pin the font sizes so every overview box matches instead of each
            # value auto-fitting to its own digit count / cell size.
            "text": {"titleSize": OVERVIEW_TITLE_SIZE, "valueSize": OVERVIEW_VALUE_SIZE},
        },
        "targets": targets,
    }


# Neutral colour for the "total" number in a merged overview stat: present but
# not alarming, so the eye goes to a non-zero red failure count next to it.
NEUTRAL = "#8e8e8e"


panels = []

# Layout: x in 0..24, y increments per row. We track y manually.
y = 0

# Row: Overview activity in the selected range, not database totals
panels.append(row("Overview", y))
y += 1

# Merged count boxes: each overview total also carries its failure (and, for
# results/hosts, unreachable) counterpart, so failures are visible at a glance
# in the overview without a separate stat row.
panels.append(multistat(
    "Playbooks",
    [("total", "ara_playbooks", NEUTRAL),
     ("failed", 'ara_playbooks{status="failed"}', "red")],
    {"h": 6, "w": 4, "x": 0, "y": y},
    description="New playbooks in the selected range, with how many failed."))
panels.append(multistat(
    "Tasks",
    [("total", "ara_tasks", NEUTRAL),
     ("failed", 'ara_tasks{status="failed"}', "red")],
    {"h": 6, "w": 4, "x": 4, "y": y},
    description="New tasks in the selected range, with how many failed."))
panels.append(multistat(
    "Results",
    [("total", "ara_results", NEUTRAL),
     ("failed", 'ara_results{status="failed"}', "red"),
     ("unreachable", 'ara_results{status="unreachable"}', "purple")],
    {"h": 6, "w": 6, "x": 8, "y": y},
    description="New task results in the selected range, with failed and unreachable counts. "
                "Excludes results with ignore_errors=True."))
panels.append(multistat(
    "Hosts",
    [("total", "ara_hosts", NEUTRAL),
     ("failed", 'ara_hosts_by_hostname{status="failed"}', "red"),
     ("unreachable", 'ara_hosts_by_hostname{status="unreachable"}', "purple")],
    {"h": 6, "w": 6, "x": 14, "y": y},
    description="New host records (one per host x playbook) in the selected range (total), plus failed "
                "and unreachable result counts summed across hosts from the per-hostname breakdown."))
panels.append(piechart(
    "Playbook outcomes",
    "sum by (status) (clamp_min(delta(ara_playbooks[$__range]), 0)) > 0.5", "{{status}}",
    {"h": 6, "w": 4, "x": 20, "y": y}, overrides=status_overrides(STATUS_COLORS),
    show_legend=False, display_labels=["name", "percent"],
    description="Composition of playbooks that ran in the selected range, each slice labelled with its "
                "status and share."))
y += 6
# Playbook and task activity side by side, both stacked terminal-status bars
# with a live "running" line on a second axis (see running_overlay_override).
# Heights across the overview are kept at h=6 so the whole section stays close
# to a single screen even with the extra task panel and the full-width results.
panels.append(timeseries(
    "Playbooks by status",
    [target("sum by (status) (%s)" % new_per_bucket('ara_playbooks{status!~"unknown|running"}'),
            legend="{{status}}", min_step=BUCKET_MIN_STEP),
     target('ara_playbooks{status="running"}', legend="running", ref="B")],
    {"h": 6, "w": 12, "x": 0, "y": y}, bars=True, stack=True,
    overrides=status_overrides(STATUS_COLORS) + running_overlay_override(),
    description="New playbooks per interval as stacked bars, split by status. "
                "Overlaid as a line on the right axis is the number of playbooks 'running'."))
panels.append(timeseries(
    "Tasks by status",
    [target("sum by (status) (%s)" % new_per_bucket('ara_tasks{status!~"unknown|running"}'),
            legend="{{status}}", min_step=BUCKET_MIN_STEP),
     target('ara_tasks{status="running"}', legend="running", ref="B")],
    {"h": 6, "w": 12, "x": 12, "y": y}, bars=True, stack=True,
    overrides=status_overrides(STATUS_COLORS) + running_overlay_override(),
    description="New tasks per interval as stacked bars, split by status. "
                "Overlaid as a line on the right axis is the number of tasks 'running'."))
y += 6
# Duration percentiles sit directly under the activity panel they complement:
# playbook percentiles under playbook activity, task percentiles under task
# activity, so each column reads volume-then-latency for the same object.
panels.append(timeseries(
    "Playbook durations",
    [target("histogram_quantile(0.50, ara_playbook_duration_seconds_bucket)", legend="p50"),
     target("histogram_quantile(0.95, ara_playbook_duration_seconds_bucket)", legend="p95", ref="B"),
     target("histogram_quantile(0.99, ara_playbook_duration_seconds_bucket)", legend="p99", ref="C"),
     target("ara_playbook_duration_seconds_max", legend="max", ref="D")],
    {"h": 6, "w": 12, "x": 0, "y": y}, unit="s", fill=0,
    description="Percentiles of playbook durations over the specified range window."))
panels.append(timeseries(
    "Task durations",
    [target("histogram_quantile(0.50, ara_task_duration_seconds_bucket)", legend="p50"),
     target("histogram_quantile(0.95, ara_task_duration_seconds_bucket)", legend="p95", ref="B"),
     target("histogram_quantile(0.99, ara_task_duration_seconds_bucket)", legend="p99", ref="C"),
     target("ara_task_duration_seconds_max", legend="max", ref="D")],
    {"h": 6, "w": 12, "x": 12, "y": y}, unit="s", fill=0,
    description="Percentiles of task durations over the specified range window."))
y += 6
panels.append(timeseries(
    "Results by status",
    [target("sum by (status) (%s)" % new_per_bucket('ara_results{status!="unknown"}'),
            legend="{{status}}", min_step=BUCKET_MIN_STEP)],
    {"h": 6, "w": 24, "x": 0, "y": y}, bars=True, stack=True,
    overrides=status_overrides(["changed", "ok", "skipped", "failed", "ignored", "unreachable"]),
    description="New task results per interval as stacked bars split by ara's derived status."))
y += 6
panels.append(timeseries(
    "Top hosts by changed results",
    [target(active_new_by("hostname", 'ara_hosts_by_hostname{status="changed"}', top=10),
            legend="{{hostname}}", min_step=BUCKET_MIN_STEP)],
    {"h": 6, "w": 12, "x": 0, "y": y}, bars=True, stack=True, legend_table=True,
    description="New changed task results per interval stacked by host for the selected time range."))
panels.append(timeseries(
    "Top hosts by failed / unreachable results",
    [target(active_new_by("hostname", 'ara_hosts_by_hostname{status=~"failed|unreachable"}', top=10),
            legend="{{hostname}}", min_step=BUCKET_MIN_STEP)],
    {"h": 6, "w": 12, "x": 12, "y": y}, bars=True, stack=True, legend_table=True,
    description="New failed and unreachable results (combined) per interval stacked by host. "
                "An empty panel means nothing failed or went unreachable in the selected window."))
y += 6

# Row: Activity by controller / user / version (who and what is running now)
panels.append(row("Activity by controller / user / version", y))
y += 1
panels.append(timeseries(
    "Playbooks by controller",
    [target(active_recorded_by("controller", "ara_recorded_playbooks_by_controller_total"),
            legend="{{controller}}", min_step=BUCKET_MIN_STEP)],
    {"h": 8, "w": 12, "x": 0, "y": y}, bars=True, stack=True, legend_table=True,
    description="Where playbooks are being run from, per interval."))
panels.append(timeseries(
    "Playbooks by user",
    [target(active_recorded_by("user", "ara_recorded_playbooks_by_user_total"), legend="{{user}}",
            min_step=BUCKET_MIN_STEP)],
    {"h": 8, "w": 12, "x": 12, "y": y}, bars=True, stack=True, legend_table=True,
    description="Who is running playbooks, per interval."))
y += 8
panels.append(timeseries(
    "Playbooks by Ansible version",
    [target(active_recorded_by("ansible_version", "ara_recorded_playbooks_by_ansible_version_total"),
            legend="{{ansible_version}}", min_step=BUCKET_MIN_STEP)],
    {"h": 8, "w": 12, "x": 0, "y": y}, bars=True, stack=True, legend_table=True,
    description="Which Ansible versions are running, per interval."))
panels.append(timeseries(
    "Playbooks by Python version",
    [target(active_recorded_by("python_version", "ara_recorded_playbooks_by_python_version_total"),
            legend="{{python_version}}", min_step=BUCKET_MIN_STEP)],
    {"h": 8, "w": 12, "x": 12, "y": y}, bars=True, stack=True, legend_table=True,
    description="Which Python versions the controllers ran Ansible under, per interval."))
y += 8

# Row: Exporter health
panels.append(row("Exporter health", y))
y += 1
panels.append(stat("ara API reachable", "ara_up", {"h": 4, "w": 6, "x": 0, "y": y},
                   thresholds=[{"color": "red", "value": None}, {"color": "green", "value": 1}],
                   mappings=[{"type": "value", "options": {
                       "0": {"text": "DOWN", "index": 0}, "1": {"text": "UP", "index": 1}}}],
                   description="UP when the exporter could reach ara on the last refresh, DOWN "
                               "otherwise. When DOWN the exporter serves the last good data, so the "
                               "activity panels flatline; the ara_up == 0 annotation shades that window. "
                               "The annotation can be toggled at the top of the dashboard."))
panels.append(stat("Scrape errors", "increase(ara_scrape_errors_total[$__range])",
                   {"h": 4, "w": 6, "x": 6, "y": y},
                   thresholds=[{"color": "green", "value": None}, {"color": "red", "value": 1}],
                   description="Refreshes that failed to collect from ara over the selected range. "))
panels.append(stat("Metrics age", "ara_metrics_age_seconds", {"h": 4, "w": 6, "x": 12, "y": y}, unit="s",
                   thresholds=[{"color": "green", "value": None}, {"color": "orange", "value": 120},
                               {"color": "red", "value": 300}],
                   description="Age of the cached metrics being served (grows if background refreshes "
                               "start failing)."))
panels.append(stat("Refresh duration", "ara_refresh_duration_seconds", {"h": 4, "w": 6, "x": 18, "y": y},
                   unit="s", color_mode="palette-classic",
                   description="Time the last background refresh spent querying ara and building metrics."))
y += 4
panels.append(timeseries(
    "Scrape & refresh duration",
    [target("ara_scrape_duration_seconds", legend="scrape (cache serve)"),
     target("ara_refresh_duration_seconds", legend="refresh (build)", ref="B")],
    {"h": 6, "w": 24, "x": 0, "y": y}, unit="s",
    description="Time to answer each scrape (served from cache, so near-zero) versus the time each "
                "background refresh spends building metrics from ara."))
y += 6

dashboard = {
    "__inputs": [
        {
            "name": "DS_PROMETHEUS",
            "label": "Prometheus",
            "description": "Prometheus data source scraping the ara exporter",
            "type": "datasource",
            "pluginId": "prometheus",
            "pluginName": "Prometheus",
        }
    ],
    "__requires": [
        {"type": "grafana", "id": "grafana", "name": "Grafana", "version": "10.0.0"},
        {"type": "datasource", "id": "prometheus", "name": "Prometheus", "version": "1.0.0"},
        {"type": "panel", "id": "timeseries", "name": "Time series", "version": ""},
        {"type": "panel", "id": "stat", "name": "Stat", "version": ""},
        {"type": "panel", "id": "piechart", "name": "Pie chart", "version": ""},
    ],
    "annotations": {"list": [
        {
            "builtIn": 1,
            "datasource": {"type": "grafana", "uid": "-- Grafana --"},
            "enable": True,
            "hide": True,
            "iconColor": "rgba(0, 211, 255, 1)",
            "name": "Annotations & Alerts",
            "type": "dashboard",
        },
        {
            # Shade the intervals where the exporter could not reach ara. Without
            # this, an outage just makes the activity panels flatline (the
            # exporter serves stale data) with no on-canvas explanation. Grafana
            # annotation toggles carry no hover tooltip (only dashboard links do),
            # so the explanation lives in titleFormat, shown when you hover a
            # shaded region, and the toggle name is kept descriptive.
            "datasource": DS,
            "enable": True,
            "hide": False,
            "iconColor": "red",
            "name": "ara unreachable (shading)",
            "expr": "ara_up == 0",
            "titleFormat": "ara API unreachable - exporter served stale data here",
            "step": "60s",
        },
    ]},
    "editable": True,
    "fiscalYearStartMonth": 0,
    "graphTooltip": 1,
    # Link back to the ara web UI, using the $ara_server template variable
    # (sourced from the ara_api_server metric emitted by the http client). The
    # dashboard time range is passed through as started_after/before so the ara
    # playbook list is scoped to the same window you are looking at.
    "links": [
        {
            "title": "ARA Prometheus docs",
            "type": "link",
            "icon": "doc",
            "url": "https://ara.readthedocs.io/en/latest/prometheus.html",
            "targetBlank": True,
            "tooltip": "Documentation for the ara prometheus exporter and its metrics",
        },
        {
            "title": "Open ara",
            "type": "link",
            "icon": "external link",
            "url": "${ara_server}",
            "targetBlank": True,
            "tooltip": "Open the ara web UI this dashboard is reading from",
        },
        {
            "title": "Failed playbooks",
            "type": "link",
            "icon": "external link",
            "url": "${ara_server}/?status=failed&started_after=${__from:date:iso}&started_before=${__to:date:iso}",
            "targetBlank": True,
            "tooltip": "Open the playbooks that failed during the selected range in the ara web UI",
        },
        {
            "title": "Failed tasks",
            "type": "link",
            "icon": "external link",
            "url": "${ara_server}/tasks?status=failed&started_after=${__from:date:iso}&started_before=${__to:date:iso}",
            "targetBlank": True,
            "tooltip": "Open the tasks that failed during the selected range in the ara web UI",
        },
        {
            "title": "Failed hosts",
            "type": "link",
            "icon": "external link",
            # Hosts carry an 'updated' time, not 'started', and the host list
            # defaults to the "latest" view where only updated_after is honoured,
            # so this scopes to hosts with a failure that were touched since the
            # range start rather than a start/end window like the two links above.
            "url": "${ara_server}/hosts?failed__gt=0&updated_after=${__from:date:iso}",
            "targetBlank": True,
            "tooltip": "Open the hosts with at least one failed result since the range start in the ara web UI",
        },
    ],
    "liveNow": False,
    "panels": panels,
    "refresh": "30s",
    "schemaVersion": 39,
    "style": "dark",
    "tags": ["ara", "ansible", "prometheus"],
    "templating": {"list": [
        {
            # Resolves to the ara web address the exporter is pointed at, from the
            # ara_api_server{server=...} metric. Used by the dashboard links
            # above. Hidden because it is plumbing, not a filter (it does not
            # scope any panel), which keeps it clear of the "no filter dropdowns"
            # decision. Empty when reading from the offline client (no web UI).
            "name": "ara_server",
            "type": "query",
            "datasource": DS,
            "query": "label_values(ara_api_server, server)",
            "refresh": 2,
            "hide": 2,
            "includeAll": False,
            "multi": False,
            "sort": 1,
        },
    ]},
    "time": {"from": "now-6h", "to": "now"},
    "timepicker": {},
    "timezone": "",
    "title": "Ansible metrics (by ara)",
    "uid": "ara-ansible-metrics",
    "version": 1,
    "weekStart": "",
}

with open("contrib/grafana/ara-dashboard.json", "w") as f:
    json.dump(dashboard, f, indent=2)
    f.write("\n")

print("wrote contrib/grafana/ara-dashboard.json with", len(panels), "panels")
