
import argparse
import csv
import json
import math
import re
import zipfile
from datetime import datetime, time
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



def parse_line(line, current_date=None):
    """Parse PBS records, infer dates and preserve quality warnings."""

    line = line.strip()
    warnings = []

    # Support comma-separated and space-separated records.
    if "," in line:
        parts = [part.strip() for part in line.split(",")]
        timestamp_text = parts[0]
        metric_parts = parts[1:]
    else:
        match = re.match(
            r"^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}|\d{2}:\d{2})\s+(.+)$",
            line,
        )

        if not match:
            raise ValueError("No metrics found")

        timestamp_text = match.group(1)
        metric_parts = match.group(2).split()

    # Parse full or time-only timestamps.
    try:
        if re.fullmatch(r"\d{2}:\d{2}", timestamp_text):
            if current_date is None:
                raise ValueError("Time-only timestamp has no known date")

            timestamp = datetime.strptime(
                current_date + " " + timestamp_text,
                "%Y-%m-%d %H:%M",
            )
            warnings.append("Date inferred from preceding dated record")
        else:
            timestamp = datetime.strptime(
                timestamp_text,
                "%Y-%m-%d %H:%M",
            )
            current_date = timestamp.strftime("%Y-%m-%d")

    except ValueError as error:
        raise ValueError(f"Invalid timestamp: {timestamp_text}") from error

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
    seen = {}

    for filename in selected_files:
        print(f"Processing: {filename}")

        lines = archive.read(filename).decode(
            "utf-8-sig",
            errors="replace",
        ).splitlines()

        current_date = None

        for line_number, line in enumerate(lines, start=1):
            if not line.strip():
                blank_lines += 1
                continue

            try:
                record, current_date, warnings = parse_line(
                    line, current_date
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

                if timestamp in seen:
                    previous = seen[timestamp]

                    same_record = all(
                        record[column] == previous["record"][column]
                        for column in COLUMNS
                    )

                    if same_record:
                        duplicate_rows.append({
                            "source_file": filename,
                            "line_number": line_number,
                            "timestamp": timestamp,
                            "reason": "Identical duplicate",
                        })
                    else:
                        conflicting_rows.append({
                            "timestamp": timestamp,
                            "kept_source": previous["source"],
                            "kept_line": previous["line"],
                            "conflict_source": filename,
                            "conflict_line": line_number,
                            "kept_record": json.dumps(
                                previous["record"]
                            ),
                            "conflict_record": json.dumps(record),
                            "reason": "Different values for same timestamp",
                        })

                    continue

                seen[timestamp] = {
                    "record": record,
                    "source": filename,
                    "line": line_number,
                }

                clean_rows.append(record)

            except (ValueError, OverflowError) as error:
                rejected_rows.append({
                    "source_file": filename,
                    "line_number": line_number,
                    "original_line": line,
                    "reason": str(error),
                })

    clean_rows.sort(key=lambda row: row["timestamp"])

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
        ["source_file", "line_number", "timestamp", "reason"],
    )

    write_csv(
        output_dir / "conflicting_snapshots.csv",
        conflicting_rows,
        [
            "timestamp",
            "kept_source",
            "kept_line",
            "conflict_source",
            "conflict_line",
            "kept_record",
            "conflict_record",
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
        "input_nonblank_rows": (
            len(clean_rows)
            + len(rejected_rows)
            + len(duplicate_rows)
            + len(conflicting_rows)
        ),
        "blank_lines": blank_lines,
        "clean_rows": len(clean_rows),
        "rejected_rows": len(rejected_rows),
        "duplicate_rows": len(duplicate_rows),
        "conflicting_timestamps": len(conflicting_rows),
        "quality_warnings": len(warning_rows),
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
- Quality warnings: {summary['quality_warnings']}

## Timestamp range

- First timestamp: {summary['first_timestamp']}
- Last timestamp: {summary['last_timestamp']}

## Cleaning rules

1. Read PBS log files from the supplied ZIP archive.
2. Support both historical log formats.
3. Require timestamp and core job and node measurements.
4. Treat optional measurements as missing when absent.
5. Convert integer and percentage measurements to numeric values.
6. Preserve CPU percentages above 100% and flag them.
7. Retain node-count inconsistencies and flag them.
8. Retain zero-node snapshots with missing percentages.
9. Infer time-only dates from the preceding dated record.
10. Reject records with invalid or missing required information.
11. Identify and record identical duplicates.
12. Preserve conflicting records for manual review.
13. Retain the first valid occurrence provisionally.
14. Sort clean snapshots chronologically.

## Important limitations

Time-only dates are inferred from the preceding dated record
within the same file. These inferred dates are flagged for review.

Conflicting snapshots are not silently discarded:
their original metric values are preserved in the conflict report.
The first valid record is retained provisionally in snapshots.csv.

The source timezone has not been established. No timezone
has been assigned to the timestamps.

Missing values remain empty; they are not replaced with zero.
Quality warnings do not automatically cause a record to be rejected.
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