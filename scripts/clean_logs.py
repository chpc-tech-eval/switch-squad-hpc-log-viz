
import argparse
import csv
import json
import math
import re
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "logs.zip"

EXPECTED_COLUMNS = [
    "timestamp",
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

    
]
COLUMNS = [
    "timestamp",
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
]

INTEGER_COLUMNS = [
    "jobs_running",
    "jobs_queued",
    "jobs_held",
    "jobs_exiting",
    "nodes_running",
    "nodes_offline",
    "nodes_total",
    "cpu_used",
    "cpu_total",
]

PERCENT_COLUMNS = [
    "nodes_running_percent",
    "cpu_percent",
]

REQUIRED_COLUMNS = [
    "jobs_running",
    "jobs_queued",
    "nodes_running",
    "nodes_offline",
    "nodes_total",
]


@dataclass
class TimestampContext:
    date: str | None = None
    previous_timestamp: datetime | None = None

    def clear(self):
        self.date = None
        self.previous_timestamp = None


def parse_line(line, current_date=None, *, context=None):
    """Parse PBS records, infer dates and preserve quality warnings."""

    if context is None:
        context = TimestampContext(date=current_date)
    current_date = context.date
    line = line.strip()
    warnings = []

    # Support comma-separated and space-separated records.
    if "," in line:
        parts = [part.strip() for part in line.split(",")]
        timestamp_text = parts[0]
        metric_parts = parts[1:]
    else:
        match = re.match(
            r"^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}|\d{2}:\d{2})(?:\s+(.+))?$",
            line,
        )

        if not match:
            context.clear()
            raise ValueError("No metrics found")

        timestamp_text = match.group(1)
        metric_parts = (match.group(2) or "").split()

    # Parse full or time-only timestamps.
    try:
        if re.fullmatch(r"\d{2}:\d{2}", timestamp_text):
            if current_date is None:
                raise ValueError("Time-only timestamp has no known date")

            timestamp = datetime.strptime(
                current_date + " " + timestamp_text,
                "%Y-%m-%d %H:%M",
            )
            if (
                context.previous_timestamp is not None
                and timestamp < context.previous_timestamp
            ):
                raise ValueError(
                    "Time-only timestamp moved backwards; an explicit date is required"
                )
            warnings.append("Date inferred from preceding explicit dated timestamp")
        else:
            timestamp = datetime.strptime(
                timestamp_text,
                "%Y-%m-%d %H:%M",
            )

    except ValueError as error:
        context.clear()
        raise ValueError(
            f"Invalid or ambiguous timestamp: {timestamp_text} ({error})"
        ) from error

    # Keep valid date context even if this row's metrics are later rejected.
    # Never guess that a backwards time-only value belongs to the next day.
    current_date = timestamp.strftime("%Y-%m-%d")
    context.date = current_date
    context.previous_timestamp = timestamp

    if not metric_parts:
        raise ValueError("No metrics found")

    record = {"timestamp": timestamp}

    for part in metric_parts:
        if "=" not in part:
            raise ValueError(f"Invalid metric: {part}")

        key, value = part.split("=", 1)
        key = key.strip()
        value = value.strip()

        if not key or key in record:
            raise ValueError(f"Empty or repeated field: {key}")

        if key not in EXPECTED_COLUMNS:
            raise ValueError(f"Unexpected field: {key}")

        record[key] = value

    missing_required = [
        column for column in REQUIRED_COLUMNS
        if record.get(column, "") == ""
    ]
    if missing_required:
        raise ValueError(
            "Missing required measurements: " + ", ".join(missing_required)
        )

    # Keep all expected columns, including missing measurements.
    for column in EXPECTED_COLUMNS:
        if column == "timestamp":
            continue

        if column not in record:
            record[column] = ""

        if record[column] == "":
            warnings.append(f"Missing measurement: {column}")

    # Convert integer measurements.
    for column in INTEGER_COLUMNS:
        value = record[column]

        if value == "":
            continue

        if not re.fullmatch(r"\d+", str(value)):
            raise ValueError(f"Invalid integer in {column}")

        record[column] = int(value)

    # Convert percentage measurements.
    for column in PERCENT_COLUMNS:
        value = record[column]

        if value == "":
            continue

        try:
            number = float(str(value).removesuffix("%").strip())
        except ValueError:
            raise ValueError(f"Invalid percentage in {column}")

        if not math.isfinite(number) or number < 0:
            raise ValueError(f"Invalid percentage in {column}")

        record[column] = number

    # Flag unusual measurements without discarding the record.
    if (
        record["nodes_total"] == 0
        and record["nodes_total"] != ""
    ):
        warnings.append("Total node count is zero")

    if (
        record["nodes_running"] != ""
        and record["nodes_offline"] != ""
        and record["nodes_total"] != ""
        and record["nodes_running"] + record["nodes_offline"]
        > record["nodes_total"]
    ):
        warnings.append("Running and offline nodes exceed total nodes")

    if (
        record["cpu_used"] != ""
        and record["cpu_total"] != ""
        and record["cpu_used"] > record["cpu_total"]
    ):
        warnings.append("CPU used exceeds total CPU")

    if (
        record["cpu_percent"] != ""
        and record["cpu_percent"] > 100
    ):
        warnings.append(
            f"cpu_percent exceeds 100%: {record['cpu_percent']}"
        )

    return record, current_date, warnings


def write_csv(path, rows, columns):
    """Write rows to a CSV file."""

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def process_files(archive, selected_files, output_dir):
    clean_rows = []
    rejected_rows = []
    duplicate_rows = []
    conflicting_rows = []
    warning_rows = []
    blank_lines = 0
    input_nonblank_rows = 0
    seen = {}
    conflicting_records = {}

    for filename in selected_files:
        print(f"Processing: {filename}")

        lines = archive.read(filename).decode(
            "utf-8-sig",
            errors="replace",
        ).splitlines()

        context = TimestampContext()

        for line_number, line in enumerate(lines, start=1):
            if not line.strip():
                blank_lines += 1
                continue

            input_nonblank_rows += 1
            try:
                record, _, warnings = parse_line(
                    line, context=context
                )

                timestamp = record["timestamp"].isoformat(
                    sep=" ", timespec="minutes"
                )
                record["timestamp"] = timestamp

                for warning in warnings:
                    warning_rows.append({
                        "source_file": filename,
                        "line_number": line_number,
                        "timestamp": timestamp,
                        "warning": warning,
                        "original_line": line,
                    })

                entry = {
                    "record": record,
                    "source": filename,
                    "line": line_number,
                }
                if timestamp not in seen:
                    seen[timestamp] = entry
                    continue

                fingerprint = tuple(record[column] for column in COLUMNS)
                if timestamp in conflicting_records:
                    previous = conflicting_records[timestamp].get(fingerprint)
                else:
                    first = seen[timestamp]
                    first_fingerprint = tuple(
                        first["record"][column] for column in COLUMNS
                    )
                    previous = first if fingerprint == first_fingerprint else None

                if previous is not None:
                    previous["occurrences"] = previous.get("occurrences", 1) + 1
                    duplicate_rows.append({
                        "source_file": filename,
                        "line_number": line_number,
                        "timestamp": timestamp,
                        "duplicate_of_source": previous["source"],
                        "duplicate_of_line": previous["line"],
                        "reason": "Identical normalised duplicate",
                    })
                else:
                    if timestamp not in conflicting_records:
                        conflicting_records[timestamp] = {
                            first_fingerprint: seen[timestamp]
                        }
                    conflicting_records[timestamp][fingerprint] = entry

            except (ValueError, OverflowError) as error:
                rejected_rows.append({
                    "source_file": filename,
                    "line_number": line_number,
                    "original_line": line,
                    "reason": str(error),
                })

    # Export no winner for an unresolved conflicting timestamp.
    clean_rows = [
        entry["record"] for timestamp, entry in seen.items()
        if timestamp not in conflicting_records
    ]
    clean_rows.sort(key=lambda row: row["timestamp"])
    for timestamp, variants in sorted(conflicting_records.items()):
        for entry in variants.values():
            conflicting_rows.append({
                "timestamp": timestamp,
                "source_file": entry["source"],
                "line_number": entry["line"],
                "record": json.dumps(entry["record"], sort_keys=True),
                "identical_occurrences": entry.get("occurrences", 1),
                "reason": "Different values for same timestamp; quarantined",
            })

    accounted_rows = (
        len(clean_rows) + len(rejected_rows)
        + len(duplicate_rows) + len(conflicting_rows)
    )
    if accounted_rows != input_nonblank_rows:
        raise RuntimeError("Input/output row accounting failed; no files were written")

    output_dir.mkdir(parents=True, exist_ok=True)

    write_csv(output_dir / "snapshots.csv", clean_rows, COLUMNS)

    write_csv(
        output_dir / "rejected_rows.csv",
        rejected_rows,
        ["source_file", "line_number", "original_line", "reason"],
    )

    write_csv(
        output_dir / "duplicate_rows.csv",
        duplicate_rows,
        [
            "source_file", "line_number", "timestamp",
            "duplicate_of_source", "duplicate_of_line", "reason",
        ],
    )

    write_csv(
        output_dir / "conflicting_snapshots.csv",
        conflicting_rows,
        [
            "timestamp",
            "source_file",
            "line_number",
            "record",
            "identical_occurrences",
            "reason",
        ],
    )

    write_csv(
        output_dir / "quality_warnings.csv",
        warning_rows,
        [
            "source_file",
            "line_number",
            "timestamp",
            "warning",
            "original_line",
        ],
    )

    summary = {
        "files_processed": len(selected_files),
        "input_nonblank_rows": input_nonblank_rows,
        "blank_lines": blank_lines,
        "clean_rows": len(clean_rows),
        "rejected_rows": len(rejected_rows),
        "duplicate_rows": len(duplicate_rows),
        "conflicting_timestamps": len(conflicting_records),
        "conflicting_variants": len(conflicting_rows),
        "quality_warnings": len(warning_rows),
        "row_accounting_ok": accounted_rows == input_nonblank_rows,
        "first_timestamp": (
            clean_rows[0]["timestamp"] if clean_rows else None
        ),
        "last_timestamp": (
            clean_rows[-1]["timestamp"] if clean_rows else None
        ),
    }

    with (output_dir / "summary.json").open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(summary, file, indent=4)

    report = f"""# HPC Log Cleaning Report

## Processing summary

- Files processed: {summary['files_processed']}
- Nonblank input rows: {summary['input_nonblank_rows']}
- Blank lines: {blank_lines}
- Clean rows: {summary['clean_rows']}
- Rejected rows: {summary['rejected_rows']}
- Identical duplicate rows: {summary['duplicate_rows']}
- Conflicting timestamps: {summary['conflicting_timestamps']}
- Conflicting variants quarantined: {summary['conflicting_variants']}
- Quality warning events: {summary['quality_warnings']}
- Input/output row accounting passed: {summary['row_accounting_ok']}

## Timestamp range of clean snapshots

- First timestamp: {summary['first_timestamp']}
- Last timestamp: {summary['last_timestamp']}

## Cleaning rules

1. Read PBS log files from the supplied ZIP archive.
2. Support both historical log formats.
3. Require a valid timestamp and nonempty jobs_running, jobs_queued,
   nodes_running, nodes_offline and nodes_total measurements.
4. Treat optional measurements as missing when absent.
5. Convert integer and percentage measurements to numeric values.
6. Preserve CPU percentages above 100% and flag them.
7. Retain node-count inconsistencies and flag them.
8. Retain zero-node snapshots with missing percentages.
9. Infer time-only dates only from an established explicit date with
   nondecreasing times. A valid dated timestamp updates date context
   even when that record's metrics are rejected.
10. Reject records with invalid or missing required information.
11. Identify and record identical duplicates.
12. Count distinct conflicting timestamps separately from their variants.
13. Quarantine every distinct variant at a conflicting timestamp;
    exclude that timestamp from snapshots.csv until resolved.
14. Sort clean snapshots chronologically.
15. Verify that nonblank input rows equal clean rows plus rejected rows
    plus extra identical duplicates plus distinct conflicting variants.

## Important limitations

Time-only dates use explicit date context within the same file.
Inferred dates are flagged for review. Backwards time-only values,
including ambiguous midnight rollovers, are rejected and clear the
date context. Following time-only records require a new explicit date.
No next-day rollover is guessed automatically.

Every distinct conflicting snapshot is preserved in the conflict report,
with source references and its number of identical occurrences.
Extra identical occurrences are listed separately in duplicate_rows.csv.
No unresolved conflicting timestamp appears in snapshots.csv.

The source timezone has not been established. No timezone
has been assigned to the timestamps.

Missing values remain empty; they are not replaced with zero.
Missing required measurements cause rejection; optional measurements
may be empty. The required-field list must agree with the schema in #5.
Quality warnings are individual events, not counts of distinct bad rows;
missing optional historical measurements also contribute warning events.
Warnings do not automatically cause a record to be rejected.
"""

    (output_dir / "cleaning_report.md").write_text(
        report, encoding="utf-8"
    )

    print("\nRUN SUMMARY")
    print(json.dumps(summary, indent=4))
    print(f"\nOutput directory: {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Clean historical PBS HPC log snapshots."
    )

    parser.add_argument(
        "--sample",
        default="logs/2017-01-22.log",
        help="Process one log file inside logs.zip",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all .log files inside logs.zip",
    )

    args = parser.parse_args()

    if not ARCHIVE.exists():
        raise FileNotFoundError(
            f"Dataset archive not found: {ARCHIVE}"
        )

    with zipfile.ZipFile(ARCHIVE) as archive:
        available_files = sorted(
            name for name in archive.namelist()
            if name.lower().endswith(".log")
        )

        if args.all:
            selected_files = available_files
            output_dir = ROOT / "data" / "cleaned"
        else:
            if args.sample not in archive.namelist():
                raise FileNotFoundError(
                    f"Sample not found inside ZIP: {args.sample}"
                )

            selected_files = [args.sample]
            output_dir = ROOT / "data" / "sample"

        if not selected_files:
            raise FileNotFoundError(
                "No .log files found inside logs.zip"
            )

        process_files(archive, selected_files, output_dir)


if __name__ == "__main__":
    main()
