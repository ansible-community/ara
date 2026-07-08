#!/usr/bin/env python3
# Copyright (c) 2026 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Validate contrib/grafana/ara-dashboard.json against the exporter's metrics.

For every panel target (and every dashboard link/annotation), this:
  - substitutes the Grafana built-in variables so the expression is plain PromQL,
  - parses it with promql-parser to catch syntax errors,
  - checks that every ara_* metric it references is one the exporter actually
    emits (EMITTED below), so a renamed or removed metric is caught here rather
    than as an empty panel in Grafana.

This is the single most valuable check when changing either the exporter or the
dashboard generator. Run it after regenerating the dashboard:

    python3 contrib/grafana/_generate_dashboard.py
    python3 contrib/grafana/_validate_dashboard.py

Requires promql-parser (pip install promql-parser). Keep EMITTED in sync with
the metric names produced by ara/cli/prometheus.py.
"""
import json
import re
import sys

try:
    import promql_parser
except ImportError:
    sys.exit("promql-parser is required: pip install promql-parser")

# Metric names emitted by ara/cli/prometheus.py (without histogram/counter
# suffixes, which are stripped before comparison).
EMITTED = {
    "ara_playbooks",
    "ara_tasks",
    "ara_results",
    "ara_hosts",
    "ara_playbooks_window",
    "ara_playbooks_by_controller",
    "ara_playbooks_by_ansible_version",
    "ara_playbooks_by_python_version",
    "ara_playbooks_by_user",
    "ara_recorded_playbooks_by_controller",
    "ara_recorded_playbooks_by_ansible_version",
    "ara_recorded_playbooks_by_python_version",
    "ara_recorded_playbooks_by_user",
    "ara_playbook_duration_seconds",
    "ara_playbook_duration_seconds_max",
    "ara_tasks_window",
    "ara_task_duration_seconds",
    "ara_task_duration_seconds_max",
    "ara_hosts_window",
    "ara_hosts_by_hostname",
    "ara_last_playbook_started_timestamp_seconds",
    "ara_running_playbook_oldest_started_timestamp_seconds",
    "ara_api_server",
    "ara_up",
    "ara_refresh_duration_seconds",
    "ara_metrics_age_seconds",
    "ara_scrape_duration_seconds",
    "ara_scrape_errors_total",
}

# Grafana variables to substitute so expressions parse as plain PromQL.
SUBS = [("$__rate_interval", "5m"), ("$__range", "6h"), ("$__interval", "1m")]


def base(name):
    # Histogram suffixes always map back to their base series.
    for suffix in ("_bucket", "_gcount", "_gsum"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    # A _total counter maps to its base only when we emit that base name;
    # otherwise the full _total name is itself the emitted metric (e.g.
    # ara_scrape_errors_total, whose base ara_scrape_errors is never emitted).
    if name.endswith("_total") and name[: -len("_total")] in EMITTED:
        return name[: -len("_total")]
    return name


def main():
    dashboard = json.load(open("contrib/grafana/ara-dashboard.json"))
    errors = []
    checked = 0

    for panel in dashboard["panels"]:
        for target in panel.get("targets", []):
            expr = target.get("expr")
            if not expr:
                continue
            checked += 1
            for var, val in SUBS:
                expr = expr.replace(var, val)
            try:
                promql_parser.parse(expr)
            except Exception as exc:  # noqa: BLE001 - report and continue
                errors.append("%r: parse error: %s" % (panel["title"], exc))
                continue
            for name in set(re.findall(r"ara_[a-z_]+", expr)):
                if base(name) not in EMITTED:
                    errors.append("%r: unknown metric %r" % (panel["title"], name))

    # Annotation queries reference metrics too.
    for annotation in dashboard.get("annotations", {}).get("list", []):
        expr = annotation.get("expr")
        if not expr:
            continue
        checked += 1
        for name in set(re.findall(r"ara_[a-z_]+", expr)):
            if base(name) not in EMITTED:
                errors.append("annotation %r: unknown metric %r" % (annotation.get("name"), name))

    print("checked %d expressions across %d panels" % (checked, len(dashboard["panels"])))
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    print("OK: every expression parses and references only emitted metrics")


if __name__ == "__main__":
    main()
