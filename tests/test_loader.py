
import csv
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from db.loader import (
    COLUMNS,
    load_snapshots,
    parse_row,
    validate_csv,
)


def make_row(**overrides):
    row = {
        "timestamp": "2025-01-01 10:00",
        "jobs_running": "10",
        "jobs_queued": "5",
        "jobs_held": "",
        "jobs_exiting": "",
        "nodes_running": "20",
        "nodes_offline": "2",
        "nodes_total": "30",
        "nodes_running_percent": "66.67",
        "cpu_used": "100",
        "cpu_total": "200",
        "cpu_percent": "50.0",
    }
    row.update(overrides)
    return row


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def test_parse_valid_row():
    result = parse_row(make_row())

    assert len(result) == 12
    assert result[1] == 10
    assert result[2] == 5
    assert result[3] is None
    assert result[4] is None
    assert result[8] == 66.67


def test_parse_missing_optional_values():
    result = parse_row(make_row(
        jobs_held="",
        jobs_exiting="",
        cpu_used="",
    ))

    assert result[3] is None
    assert result[4] is None
    assert result[9] is None


def test_parse_negative_measurement():
    with pytest.raises(ValueError):
        parse_row(make_row(jobs_running="-1"))


def test_parse_invalid_timestamp():
    with pytest.raises(ValueError):
        parse_row(make_row(timestamp="not-a-date"))


def test_parse_invalid_integer():
    with pytest.raises(ValueError):
        parse_row(make_row(jobs_running="abc"))


def test_parse_infinite_percentage():
    with pytest.raises(ValueError):
        parse_row(make_row(cpu_percent="inf"))


def test_validate_csv_header(tmp_path):
    path = tmp_path / "snapshots.csv"
    write_csv(path, [make_row()])

    validate_csv(path)


def test_reject_invalid_csv_header(tmp_path):
    path = tmp_path / "snapshots.csv"
    path.write_text("wrong,header\n1,2\n", encoding="utf-8")

    with pytest.raises(ValueError):
        validate_csv(path)


def test_load_valid_batch(tmp_path):
    path = tmp_path / "snapshots.csv"
    error_log = tmp_path / "errors.csv"

    write_csv(path, [make_row(), make_row(
        timestamp="2025-01-01 10:05"
    )])

    connection = MagicMock()

    with patch(
        "db.loader.execute_values",
        return_value=[
            ("2025-01-01 10:00",),
            ("2025-01-01 10:05",),
        ],
    ):
        result = load_snapshots(
            connection,
            path,
            batch_size=2,
            error_log=error_log,
        )

    assert result["source_rows"] == 2
    assert result["inserted"] == 2
    assert result["skipped_duplicates"] == 0
    assert result["failed"] == 0
    assert result["accounting_ok"] is True


def test_skip_duplicate_timestamps(tmp_path):
    path = tmp_path / "snapshots.csv"
    error_log = tmp_path / "errors.csv"

    write_csv(path, [make_row(), make_row(
        timestamp="2025-01-01 10:05"
    )])

    connection = MagicMock()

    with patch(
        "db.loader.execute_values",
        return_value=[("2025-01-01 10:00",)],
    ):
        result = load_snapshots(
            connection,
            path,
            batch_size=2,
            error_log=error_log,
        )

    assert result["inserted"] == 1
    assert result["skipped_duplicates"] == 1
    assert result["accounting_ok"] is True


def test_log_invalid_rows(tmp_path):
    path = tmp_path / "snapshots.csv"
    error_log = tmp_path / "errors.csv"

    write_csv(path, [
        make_row(),
        make_row(
            timestamp="2025-01-01 10:05",
            jobs_running="-5",
        ),
    ])

    connection = MagicMock()

    with patch(
        "db.loader.execute_values",
        return_value=[("2025-01-01 10:00",)],
    ):
        result = load_snapshots(
            connection,
            path,
            batch_size=2,
            error_log=error_log,
        )

    assert result["source_rows"] == 2
    assert result["inserted"] == 1
    assert result["failed"] == 1
    assert result["accounting_ok"] is True

    with error_log.open(encoding="utf-8") as file:
        errors = list(csv.DictReader(file))

    assert len(errors) == 1
    assert errors[0]["error_type"] == "ValueError"