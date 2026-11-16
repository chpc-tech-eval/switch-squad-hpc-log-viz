"""Real TimescaleDB tests. TEST_DATABASE_DSN must name a disposable database."""
import os
from pathlib import Path

import psycopg2
import pytest

from db.loader import load_snapshots
from test_loader import make_row, write_csv


@pytest.fixture
def database():
    dsn = os.getenv("TEST_DATABASE_DSN")
    if not dsn:
        pytest.skip("Set TEST_DATABASE_DSN to a disposable database")
    connection = psycopg2.connect(dsn)
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(Path("db/schema.sql").read_text())
            cursor.execute("TRUNCATE public.cluster_snapshots")
    yield connection
    connection.close()


def test_load_repeat_conflict_and_invalid(database, tmp_path):
    source = tmp_path / "snapshots.csv"
    errors = tmp_path / "errors.csv"
    rows = [make_row(), make_row(timestamp="2025-01-01 10:05", cpu_used="")]
    write_csv(source, rows)
    first = load_snapshots(database, source, batch_size=2, error_log=errors)
    assert first["inserted"] == 2 and first["failed"] == 0
    repeat = load_snapshots(database, source, error_log=errors)
    assert repeat["inserted"] == 0 and repeat["skipped_duplicates"] == 2
    write_csv(source, [make_row(jobs_running="999"), make_row(timestamp="2025-01-01 10:10")])
    conflict = load_snapshots(database, source, error_log=errors)
    assert conflict["inserted"] == 1 and conflict["failed"] == 1
    assert "ConflictingSnapshot" in errors.read_text()
    with database.cursor() as cursor:
        cursor.execute('SELECT jobs_running FROM public.cluster_snapshots ORDER BY "timestamp"')
        assert cursor.fetchall() == [(10,), (10,), (10,)]
    write_csv(source, [make_row(jobs_running=""), make_row(cpu_used="9223372036854775808")])
    invalid = load_snapshots(database, source, error_log=errors)
    assert invalid["failed"] == 2 and invalid["inserted"] == 0


def test_batch_constraint_failure_rolls_back_then_recovers(database, tmp_path):
    source = tmp_path / "snapshots.csv"
    errors = tmp_path / "errors.csv"
    with database:
        with database.cursor() as cursor:
            cursor.execute("ALTER TABLE public.cluster_snapshots ADD CONSTRAINT test_jobs_limit CHECK (jobs_running < 100)")
    try:
        write_csv(source, [make_row(), make_row(timestamp="2025-01-01 10:05", jobs_running="999")])
        result = load_snapshots(database, source, error_log=errors)
        assert result["inserted"] == 1 and result["failed"] == 1 and result["accounting_ok"]
        with database.cursor() as cursor:
            cursor.execute("SELECT count(*) FROM public.cluster_snapshots")
            assert cursor.fetchone()[0] == 1
    finally:
        with database:
            with database.cursor() as cursor:
                cursor.execute("ALTER TABLE public.cluster_snapshots DROP CONSTRAINT test_jobs_limit")
