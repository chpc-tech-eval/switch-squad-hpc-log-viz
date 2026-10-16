
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter
import json
import re

ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT / "logs"
DOCS_DIR = ROOT / "docs"

JSON_OUTPUT = DOCS_DIR / "inventory_results.json"
REPORT_OUTPUT = DOCS_DIR / "dataset_inventory.md"

EXPECTED_FIELDS = {
    "jobs_running",
    "jobs_queued",
    "jobs_held",
    "jobs_exiting",
    "nodes_running",
    "nodes_offline",
    "nodes_total",
    "nodes_running_percent",
    "cpu_used",
    "cpu_total",
    "cpu_percent",
}

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M"
EXPECTED_INTERVAL_MINUTES = 5
EXPECTED_DAILY_RECORDS = 288


def inspect_log(path):
    """Inspect one historical HPC log without changing it."""
    result = {
        "path": path.relative_to(ROOT).as_posix(),
        "size_bytes": path.stat().st_size,
        "records": 0,
        "valid_timestamps": 0,
        "malformed_lines": [],
        "missing_fields": [],
        "duplicate_timestamps": [],
        "timestamp_gaps": [],
        "unexpected_intervals": [],
        "duplicate_lines": [],
        "missing_values": [],
        "first_timestamp": None,
        "last_timestamp": None,
        "line_count": 0,
    }

    if path.stat().st_size == 0:
        result["empty_file"] = True
        return result

    result["empty_file"] = False
    seen_lines = Counter()
    seen_timestamps = set()
    timestamps = []

    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        result["read_error"] = str(exc)
        return result

    result["line_count"] = len(lines)

    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()

        if not stripped:
            result["malformed_lines"].append({
                "line": line_number,
                "reason": "Blank line",
            })
            continue

        seen_lines[stripped] += 1
        if seen_lines[stripped] == 2:
            result["duplicate_lines"].append(line_number)

        parts = stripped.split(",", 1)
        if len(parts) != 2:
            result["malformed_lines"].append({
                "line": line_number,
                "reason": "Expected timestamp followed by comma-separated fields",
            })
            continue

        try:
            timestamp = datetime.strptime(parts[0].strip(), TIMESTAMP_FORMAT)
        except ValueError:
            result["malformed_lines"].append({
                "line": line_number,
                "reason": "Invalid timestamp format",
            })
            continue

        values = {}
        bad_pair = False

        for item in parts[1].split(","):
            if "=" not in item:
                result["malformed_lines"].append({
                    "line": line_number,
                    "reason": f"Invalid key-value item: {item.strip()}",
                })
                bad_pair = True
                continue

            key, value = item.split("=", 1)
            key = key.strip()
            value = value.strip()

            if not key:
                result["malformed_lines"].append({
                    "line": line_number,
                    "reason": "Empty field name",
                })
                bad_pair = True
                continue

            if key in values:
                result["malformed_lines"].append({
                    "line": line_number,
                    "reason": f"Duplicate field name: {key}",
                })
                bad_pair = True
                continue

            values[key] = value

            if value == "":
                result["missing_values"].append({
                    "line": line_number,
                    "field": key,
                })

        missing = sorted(EXPECTED_FIELDS - set(values))
        if missing:
            result["missing_fields"].append({
                "line": line_number,
                "fields": missing,
            })

        unexpected = sorted(set(values) - EXPECTED_FIELDS)
        if unexpected:
            result.setdefault("unexpected_fields", []).append({
                "line": line_number,
                "fields": unexpected,
            })

        # Check that metric values are numeric; percentages may include %.
        for key, value in values.items():
            if key.endswith("_percent"):
                numeric_value = value.removesuffix("%")
            else:
                numeric_value = value

            if numeric_value and not re.fullmatch(r"-?\d+(\.\d+)?", numeric_value):
                result.setdefault("non_numeric_values", []).append({
                    "line": line_number,
                    "field": key,
                    "value": value,
                })

        result["records"] += 1

        if timestamp in seen_timestamps:
            result["duplicate_timestamps"].append({
                "line": line_number,
                "timestamp": timestamp.strftime(TIMESTAMP_FORMAT),
            })
        else:
            seen_timestamps.add(timestamp)

        timestamps.append((timestamp, line_number))

        if bad_pair:
            # Details were already recorded above.
            pass

    result["valid_timestamps"] = len(timestamps)

    if timestamps:
        result["first_timestamp"] = min(t[0] for t in timestamps).strftime(
            TIMESTAMP_FORMAT
        )
        result["last_timestamp"] = max(t[0] for t in timestamps).strftime(
            TIMESTAMP_FORMAT
        )

    # Check the chronological interval between consecutive timestamps.
    ordered = sorted(timestamps)
    for (previous, previous_line), (current, current_line) in zip(
        ordered, ordered[1:]
    ):
        difference = current - previous

        if difference > timedelta(minutes=EXPECTED_INTERVAL_MINUTES):
            result["timestamp_gaps"].append({
                "from": previous.strftime(TIMESTAMP_FORMAT),
                "to": current.strftime(TIMESTAMP_FORMAT),
                "minutes": int(difference.total_seconds() / 60),
            })
        elif difference < timedelta(minutes=EXPECTED_INTERVAL_MINUTES):
            result["unexpected_intervals"].append({
                "from": previous.strftime(TIMESTAMP_FORMAT),
                "to": current.strftime(TIMESTAMP_FORMAT),
                "minutes": int(difference.total_seconds() / 60),
            })

    result["expected_daily_records"] = EXPECTED_DAILY_RECORDS
    result["record_count_differs_from_expected"] = (
        result["line_count"] != EXPECTED_DAILY_RECORDS
    )

    return result


def main():
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    log_files = sorted(
        (p for p in LOG_DIR.glob("*.log") if p.is_file()),
        key=lambda p: p.name,
    )

    results = [inspect_log(path) for path in log_files]

    nonempty = [r for r in results if not r.get("empty_file", False)]
    all_timestamps = [
        datetime.strptime(r[key], TIMESTAMP_FORMAT)
        for r in results
        for key in ("first_timestamp", "last_timestamp")
        if r.get(key)
    ]

    def total(key):
        return sum(len(r.get(key, [])) for r in results)

    summary = {
        "log_file_count": len(results),
        "empty_file_count": sum(r.get("empty_file", False) for r in results),
        "nonempty_file_count": len(nonempty),
        "files_with_unexpected_line_count": sum(
            r.get("record_count_differs_from_expected", False)
            for r in nonempty
        ),
        "total_records": sum(r.get("records", 0) for r in results),
        "malformed_line_count": total("malformed_lines"),
        "missing_field_line_count": total("missing_fields"),
        "missing_value_count": total("missing_values"),
        "duplicate_timestamp_count": total("duplicate_timestamps"),
        "duplicate_line_count": total("duplicate_lines"),
        "timestamp_gap_count": total("timestamp_gaps"),
        "unexpected_interval_count": total("unexpected_intervals"),
        "non_numeric_value_count": total("non_numeric_values"),
        "unexpected_field_count": total("unexpected_fields"),
    }

    # Derive the real timestamp range from inspected records.
    timestamps = []
    for result in results:
        for key in ("first_timestamp", "last_timestamp"):
            if result.get(key):
                timestamps.append(
                    datetime.strptime(result[key], TIMESTAMP_FORMAT)
                )

    date_range = {
        "first_timestamp": min(timestamps).strftime(TIMESTAMP_FORMAT)
        if timestamps else None,
        "last_timestamp": max(timestamps).strftime(TIMESTAMP_FORMAT)
        if timestamps else None,
    }

    output = {
        "dataset_location": "logs/*.log within the project repository",
        "format": "Plain-text log files; each record contains a timestamp and comma-separated key=value metrics",
        "expected_snapshot_interval_minutes": EXPECTED_INTERVAL_MINUTES,
        "expected_records_per_full_day": EXPECTED_DAILY_RECORDS,
        "expected_metric_fields": sorted(EXPECTED_FIELDS),
        "summary": summary,
        "timestamp_range": date_range,
        "files": results,
    }

    JSON_OUTPUT.write_text(
        json.dumps(output, indent=2),
        encoding="utf-8",
    )

    report = f"""# Historical HPC Snapshot Dataset Inventory

## Source and access

- **Repository location:** `logs/*.log`
- **Access method:** Read the plain-text log files from the local repository checkout.
- **Archive:** `logs.zip` is also present in the repository root.
- **Inspection script:** `scripts/inventory.py`
- **Machine-readable results:** `docs/inventory_results.json`

## Dataset structure

- **Log files:** {summary['log_file_count']}
- **Non-empty files:** {summary['nonempty_file_count']}
- **Empty files:** {summary['empty_file_count']}
- **Total records parsed with valid timestamps:** {summary['total_records']}
- **First valid timestamp:** {date_range['first_timestamp'] or 'Not found'}
- **Last valid timestamp:** {date_range['last_timestamp'] or 'Not found'}
- **Expected snapshot interval:** {EXPECTED_INTERVAL_MINUTES} minutes
- **Expected records in a complete 24-hour day:** {EXPECTED_DAILY_RECORDS}

Each non-empty log record is expected to contain a timestamp in
`YYYY-MM-DD HH:MM` format followed by comma-separated `key=value` metrics.

Expected metrics:

{chr(10).join('- `' + field + '`' for field in sorted(EXPECTED_FIELDS))}

## Data-quality checks

The inventory script checks blank or malformed records, missing fields,
empty values, unexpected fields, non-numeric metric values, duplicate lines,
duplicate timestamps, timestamp gaps, intervals shorter than five minutes,
and daily files whose line counts differ from 288.

| Check | Count |
|---|---:|
| Empty files | {summary['empty_file_count']} |
| Files with line counts other than 288 | {summary['files_with_unexpected_line_count']} |
| Malformed lines | {summary['malformed_line_count']} |
| Lines missing expected fields | {summary['missing_field_line_count']} |
| Empty metric values | {summary['missing_value_count']} |
| Duplicate timestamps | {summary['duplicate_timestamp_count']} |
| Duplicate lines | {summary['duplicate_line_count']} |
| Timestamp gaps over five minutes | {summary['timestamp_gap_count']} |
| Intervals shorter than five minutes | {summary['unexpected_interval_count']} |
| Non-numeric metric values | {summary['non_numeric_value_count']} |
| Records with unexpected fields | {summary['unexpected_field_count']} |

## Interpretation and limitations

A complete day sampled every five minutes should contain 288 records.
Files with different counts are candidates for incomplete days, missing
snapshots, extra records, or irregular collection. The count alone does not
prove which explanation applies; timestamp checks provide additional evidence.

The inventory describes the data as found and does not modify the source logs.
Review individual file details in `inventory_results.json` when investigating
specific anomalies.
"""

    REPORT_OUTPUT.write_text(report, encoding="utf-8")

    print("Inventory complete.")
    print(f"Log files inspected: {summary['log_file_count']}")
    print(f"Empty files: {summary['empty_file_count']}")
    print(f"Records parsed: {summary['total_records']}")
    print(f"Malformed lines: {summary['malformed_line_count']}")
    print(f"Timestamp gaps: {summary['timestamp_gap_count']}")
    print(f"JSON results: {JSON_OUTPUT.relative_to(ROOT)}")
    print(f"Markdown report: {REPORT_OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
