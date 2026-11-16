"""Generate the provisioned Grafana dashboard; no external Python packages needed."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DS = {"type": "grafana-postgresql-datasource", "uid": "hpc-timescale"}
PANELS = []


def panel(title, kind, x, y, w, h, query=None, unit="short", description=""):
    item = {
        "id": len(PANELS) + 1, "title": title, "type": kind,
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "description": description,
        "fieldConfig": {"defaults": {"unit": unit, "color": {"mode": "palette-classic"},
            "custom": {"spanNulls": False, "lineWidth": 2, "fillOpacity": 8}}, "overrides": []},
        "options": {"legend": {"displayMode": "list", "placement": "bottom"},
                    "tooltip": {"mode": "multi", "sort": "none"}},
    }
    if query:
        item["datasource"] = DS
        item["targets"] = [{"refId": "A", "datasource": DS, "rawSql": query,
                            "format": "time_series" if kind == "timeseries" else "table", "rawQuery": True}]
    PANELS.append(item)
    return item


note = panel("SWITCH SQUAD  /  Historical cluster observatory", "text", 0, 0, 24, 4)
note["options"] = {"mode": "markdown", "content": "## Eight years of cluster snapshots\nExplore reported CPU, nodes and job backlog. Change the **date range** and **bucket** above; drag across a chart to zoom.\n\n**Source wall-clock time; timezone unconfirmed.** UTC display is a plotting convention only. These are cluster aggregates: per-node usage, memory, job throughput and waiting times are unavailable. Averages weight observed snapshots equally. Missing buckets stay empty; percentages above 100% are retained."}
filter_sql = ' FROM public.cluster_snapshots WHERE $__timeFilter("timestamp")'
for title, expression, x, unit in [
    ("Accepted snapshots in range", "count(*)", 0, "short"),
    ("Mean reported CPU", "avg(cpu_percent)", 6, "percent"),
    ("Peak queued-job count", "max(jobs_queued)", 12, "short"),
    ("Snapshots missing CPU", "count(*) FILTER (WHERE cpu_percent IS NULL)", 18, "short"),
]:
    item = panel(title, "stat", x, 4, 6, 4, 'SELECT ' + expression + ' AS "value"' + filter_sql, unit)
    item["options"] = {"reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False}, "colorMode": "value", "graphMode": "none", "textMode": "auto"}
    item["fieldConfig"]["defaults"].update({"unit": "percent" if unit == "percent" else "none", "decimals": 2 if unit == "percent" else 0})


def trend(title, fields, x, y, unit="short"):
    expressions = ', '.join(f'avg({field}) AS "{label}"' for field, label in fields)
    aliases = ', '.join(f'"{label}"' for _, label in fields)
    query = 'SELECT bucket AT TIME ZONE \'UTC\' AS "time", ' + aliases + ' FROM (SELECT time_bucket_gapfill(\'${bucket}\'::interval, "timestamp") AS bucket, ' + expressions + filter_sql + ' GROUP BY 1) series ORDER BY 1'
    return panel(title, "timeseries", x, y, 12, 9, query, unit,
                 "Snapshot means per selected bucket. Source timezone unknown; no gap filling. Job counts are not throughput or waiting time.")


trend("Reported CPU percentage", [("cpu_percent", "Reported CPU %")], 0, 8, "percent")
trend("Jobs: occupancy and backlog", [("jobs_running", "Running"), ("jobs_queued", "Queued"), ("jobs_held", "Held"), ("jobs_exiting", "Exiting")], 12, 8)
trend("Nodes: reported counts", [("nodes_running", "Running nodes"), ("nodes_offline", "Offline nodes"), ("nodes_total", "Total nodes")], 0, 17)
trend("Running-node percentage", [("nodes_running_percent", "Reported running-node %")], 12, 17, "percent")
panel("Observation coverage by bucket", "timeseries", 0, 26, 12, 8,
      'SELECT bucket AT TIME ZONE \'UTC\' AS "time", "Snapshots", "CPU-present snapshots" FROM (SELECT time_bucket_gapfill(\'${bucket}\'::interval, "timestamp") AS bucket, count(*) AS "Snapshots", count(cpu_percent) AS "CPU-present snapshots"' + filter_sql + ' GROUP BY 1) series ORDER BY 1')
panel("Hour-of-day pattern (source clock)", "table", 12, 26, 12, 8,
      'SELECT extract(hour FROM "timestamp")::int AS "Hour", count(*) AS "Snapshots", count(cpu_percent) AS "CPU samples", avg(cpu_percent) AS "Mean reported CPU %", avg(jobs_queued) AS "Mean queued jobs"' + filter_sql + ' GROUP BY 1 ORDER BY 1')
panel("Peak daily means · at least 200 CPU samples", "table", 0, 34, 12, 8,
      'SELECT time_bucket(\'1 day\', "timestamp") AS "Source day", count(cpu_percent) AS "CPU samples", avg(cpu_percent) AS "Mean reported CPU %", max(jobs_queued) AS "Peak queued jobs"' + filter_sql + ' GROUP BY 1 HAVING count(cpu_percent) >= 200 ORDER BY 3 DESC, 1 LIMIT 10')
panel("Weekday patterns · Monday = 1", "table", 12, 34, 12, 8,
      'SELECT extract(isodow FROM "timestamp")::int AS "Weekday", count(*) AS "Snapshots", count(cpu_percent) AS "CPU samples", avg(cpu_percent) AS "Mean reported CPU %", avg(jobs_queued) AS "Mean queued jobs"' + filter_sql + ' GROUP BY 1 ORDER BY 1')
quality = panel("Data quality and interpretation", "text", 0, 42, 24, 5)
quality["options"] = {"mode": "markdown", "content": "### Read the gaps as carefully as the peaks\nThe supplied archive produced **903,522 accepted snapshots**, **12,489 extra identical duplicates**, **937 conflicting timestamps** (all variants quarantined), and **1 rejected row**. These are full-archive cleaning totals, independent of the selected range.\n\nCPU units and collection semantics remain unconfirmed. Zero reported CPU does not prove hardware idleness. Cluster capacity changed across the archive. The daily peak table uses a 200 CPU-sample threshold (a usual five-minute day has 288 samples). Compare narrower periods before drawing operational conclusions. See `docs/analysis.md` and the companion quality CSVs."}

# Give the caveat room at typical laptop widths.
PANELS[0]["gridPos"]["h"] = 5
for item in PANELS[1:]:
    item["gridPos"]["y"] += 1

dashboard = {
    "uid": "switch-squad-hpc", "title": "Switch Squad · Cluster history", "tags": ["SCC", "PBS", "historical"],
    "schemaVersion": 41, "version": 1, "editable": False, "timezone": "utc",
    "time": {"from": "2017-01-22T08:25:00Z", "to": "2025-10-03T15:10:00Z"},
    "refresh": "", "panels": PANELS,
    "templating": {"list": [{"name": "bucket", "label": "Bucket", "type": "custom", "query": "1 hour,1 day,1 week",
        "current": {"text": "1 day", "value": "1 day"}, "options": [
            {"text": value, "value": value, "selected": value == "1 day"} for value in ("1 hour", "1 day", "1 week")]}]},
}

if __name__ == "__main__":
    path = ROOT / "grafana/dashboards/cluster.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dashboard, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(path)
