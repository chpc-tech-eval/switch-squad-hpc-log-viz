
"""Load cleaned HPC snapshots into PostgreSQL/TimescaleDB."""

import argparse
import csv
import json
import logging
import math
import os
import sys
from datetime import datetime
from pathlib import Path

import psycopg2
from psycopg2 import DataError, IntegrityError
from psycopg2.extras import execute_values


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CSV = PROJECT_ROOT / "data" / "cleaned" / "snapshots.csv"
DEFAULT_SUMMARY = PROJECT_ROOT / "data" / "cleaned" / "summary.json"
ERROR_LOG = PROJECT_ROOT / "data" / "cleaned" / "ingestion_errors.csv"

COLUMNS = (
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
)

INTEGER_COLUMNS = {
    "jobs_running",
    "jobs_queued",
    "jobs_held",
    "jobs_exiting",
    "nodes_running",
    "nodes_offline",
    "nodes_total",
    "cpu_used",
    "cpu_total",
}

FLOAT_COLUMNS = {
    "nodes_running_percent",
    "cpu_percent",
}

INSERT_SQL = """
    INSERT INTO public.cluster_snapshots (
        "timestamp", jobs_running, jobs_queued, jobs_held,
        jobs_exiting, nodes_running, nodes_offline, nodes_total,
        nodes_running_percent, cpu_used, cpu_total, cpu_percent
    )
    VALUES %s
    ON CONFLICT ("timestamp") DO NOTHING
    RETURNING "timestamp"
"""


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def parse_row(row):
    """Convert CSV strings into database-compatible values."""

    timestamp = datetime.strptime(
        row["timestamp"], "%Y-%m-%d %H:%M"
    )

    values = [timestamp]

    for column in COLUMNS[1:]:
        raw_value = row[column].strip()

        if raw_value == "":
            values.append(None)
            continue

        if column in INTEGER_COLUMNS:
            value = int(raw_value)
            if value < 0:
                raise ValueError(f"{column} cannot be negative")
        elif column in FLOAT_COLUMNS:
            value = float(raw_value)
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"{column} must be finite and non-negative")
        else:
            raise ValueError(f"Unexpected column: {column}")

        values.append(value)

    return tuple(values)


def validate_csv(path):
    """Check that the CSV contains the expected columns."""

    with path.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.reader(file)
        header = next(reader, None)

    if header != list(COLUMNS):
        raise ValueError(
            f"Unexpected CSV header.\n"
            f"Expected: {list(COLUMNS)}\n"
            f"Received: {header}"
        )


def log_error(writer, row_number, timestamp, error):
    writer.writerow([
        row_number,
        timestamp,
        type(error).__name__,
        str(error).replace("\n", " ")[:1000],
    ])


def load_snapshots(
    connection,
    csv_path,
    batch_size=5000,
    error_log=ERROR_LOG,
):
    """Load CSV records in batches, skipping existing timestamps."""

    if batch_size < 1:
        raise ValueError("Batch size must be greater than zero")

    validate_csv(csv_path)

    error_log.parent.mkdir(parents=True, exist_ok=True)
    write_header = not error_log.exists() or error_log.stat().st_size == 0

    source_rows = 0
    inserted = 0
    skipped = 0
    failed = 0

    batch = []

    with error_log.open(
        "a", newline="", encoding="utf-8"
    ) as error_file:
        error_writer = csv.writer(error_file)

        if write_header:
            error_writer.writerow([
                "csv_row",
                "timestamp",
                "error_type",
                "error_message",
            ])

        with csv_path.open(
            "r", newline="", encoding="utf-8-sig"
        ) as file:
            reader = csv.DictReader(file)

            def process_batch(records):
                nonlocal inserted, skipped, failed

                if not records:
                    return

                try:
                    with connection:
                        with connection.cursor() as cursor:
                            returned = execute_values(
                                cursor,
                                INSERT_SQL,
                                [record[1] for record in records],
                                page_size=len(records),
                                fetch=True,
                            )

                    batch_inserted = len(returned)
                    inserted += batch_inserted
                    skipped += len(records) - batch_inserted

                except (IntegrityError, DataError):
                    # Retry individually to identify invalid records.
                    logging.warning(
                        "Batch failed validation; retrying %s rows individually.",
                        len(records),
                    )

                    for row_number, values in records:
                        try:
                            with connection:
                                with connection.cursor() as cursor:
                                    cursor.execute(
                                        INSERT_SQL.replace(
                                            "VALUES %s",
                                            "VALUES (%s, %s, %s, %s, "
                                            "%s, %s, %s, %s, %s, %s, %s, %s)",
                                        ),
                                        values,
                                    )
                                    result = cursor.fetchone()

                            if result is None:
                                skipped += 1
                            else:
                                inserted += 1

                        except (IntegrityError, DataError) as error:
                            failed += 1
                            log_error(
                                error_writer,
                                row_number,
                                values[0],
                                error,
                            )
                            logging.error(
                                "Rejected CSV row %s: %s",
                                row_number,
                                error,
                            )

            for row_number, row in enumerate(reader, start=2):
                source_rows += 1

                try:
                    values = parse_row(row)
                    batch.append((row_number, values))

                except (ValueError, TypeError, KeyError) as error:
                    failed += 1
                    log_error(
                        error_writer,
                        row_number,
                        row.get("timestamp", ""),
                        error,
                    )

                if len(batch) >= batch_size:
                    process_batch(batch)
                    batch.clear()

            if batch:
                process_batch(batch)

    return {
        "source_rows": source_rows,
        "inserted": inserted,
        "skipped_duplicates": skipped,
        "failed": failed,
        "accounting_ok": (
            source_rows == inserted + skipped + failed
        ),
    }


def verify_database(connection):
    """Return the total number of records in the destination table."""

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM public.cluster_snapshots"
        )
        return cursor.fetchone()[0]


def main():
    configure_logging()

    parser = argparse.ArgumentParser(
        description="Load cleaned HPC snapshots into TimescaleDB."
    )

    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--batch-size", type=int, default=5000)

    args = parser.parse_args()

    if not args.csv.is_file():
        parser.error(f"CSV file not found: {args.csv}")

    if not args.summary.is_file():
        parser.error(f"Summary file not found: {args.summary}")

    if args.batch_size < 1:
        parser.error("Batch size must be greater than zero")

    try:
        with args.summary.open("r", encoding="utf-8") as file:
            expected = json.load(file)["clean_rows"]

        password = os.environ.get("POSTGRES_PASSWORD")
        if not password:
            raise ValueError(
                "POSTGRES_PASSWORD environment variable is required."
            )

        connection = psycopg2.connect(
            host=os.environ.get("PGHOST", "localhost"),
            port=int(os.environ.get("PGPORT", "5433")),
            dbname=os.environ.get("PGDATABASE", "hpc_logs"),
            user=os.environ.get("PGUSER", "hpc_admin"),
            password=password,
            connect_timeout=10,
        )

        try:
            results = load_snapshots(
                connection,
                args.csv,
                batch_size=args.batch_size,
            )

            database_total = verify_database(connection)

        finally:
            connection.close()

        results["expected_clean_rows"] = expected
        results["expected_rows_match"] = (
            results["source_rows"] == expected
        )
        results["database_total_rows"] = database_total

        print("\nINGESTION SUMMARY")
        print(json.dumps(results, indent=4))

        if not results["accounting_ok"]:
            sys.exit(1)

        if not results["expected_rows_match"]:
            logging.error("Source row count does not match cleaning summary.")
            sys.exit(1)

        if results["failed"] > 0:
            logging.error("Some records failed ingestion.")
            sys.exit(1)

        logging.info("Ingestion completed successfully.")

    except (psycopg2.Error, OSError, ValueError, KeyError) as error:
        logging.exception("Ingestion stopped: %s", error)
        sys.exit(1)


if __name__ == "__main__":
    main()