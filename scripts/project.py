"""Cross-platform project commands; run as python -m scripts.project COMMAND."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import uuid

import psycopg2
from psycopg2 import sql

from db.loader import load_snapshots, parse_row

ROOT = Path(__file__).resolve().parents[1]


def environment():
    path = ROOT / ".env"
    if path.exists():
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            if line.strip() and not line.lstrip().startswith("#"):
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def connect(database=None):
    environment()
    return psycopg2.connect(
        host=os.getenv("PGHOST", "127.0.0.1"), port=os.getenv("PGPORT", "5433"),
        user=os.getenv("PGUSER", "hpc_admin"), dbname=database or os.getenv("PGDATABASE", "hpc_logs"),
        password=os.environ["POSTGRES_PASSWORD"], connect_timeout=10,
    )


def init_env():
    environment()
    path = ROOT / ".env"
    missing = [key for key in ("POSTGRES_PASSWORD", "GRAFANA_DB_PASSWORD", "GRAFANA_ADMIN_PASSWORD") if not os.getenv(key)]
    with path.open("a", encoding="utf-8") as file:
        for key in missing:
            file.write(f"\n{key}={secrets.token_hex(24)}\n")
    print("Environment file ready; existing credentials preserved. No secrets printed.")


def setup(connection):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute((ROOT / "db/schema.sql").read_text())
            cursor.execute("SELECT 1 FROM pg_roles WHERE rolname='grafana_reader'")
            if not cursor.fetchone():
                cursor.execute("CREATE ROLE grafana_reader LOGIN")
            cursor.execute(sql.SQL("ALTER ROLE grafana_reader PASSWORD {}").format(sql.Literal(os.environ["GRAFANA_DB_PASSWORD"])))
            cursor.execute("GRANT CONNECT ON DATABASE hpc_logs TO grafana_reader")
            cursor.execute("GRANT USAGE ON SCHEMA public TO grafana_reader")
            cursor.execute("GRANT SELECT ON public.cluster_snapshots TO grafana_reader")
    print("Schema and read-only Grafana role ready.")


def verify(connection):
    path = ROOT / "data/cleaned/snapshots.csv"
    matched = 0
    samples = []
    digest = hashlib.sha256()
    with path.open(newline="", encoding="utf-8-sig") as file:
        with connection.cursor(name="verify_stream") as cursor:
            cursor.itersize = 10000
            cursor.execute('SELECT * FROM public.cluster_snapshots ORDER BY "timestamp"')
            stored_rows = iter(cursor)
            for row in csv.DictReader(file):
                expected = parse_row(row)
                actual = next(stored_rows, None)
                if actual is None or tuple(actual) != expected:
                    raise ValueError(f"Database differs from cleaned CSV at data row {matched + 1}")
                matched += 1
                digest.update((repr(expected) + "\n").encode())
                if matched in (1, 100000, 500000):
                    samples.append(dict(zip(row, actual)))
            if next(stored_rows, None) is not None:
                raise ValueError("Database contains extra rows beyond canonical CSV")
    output = {
        "rows_compared": matched, "all_12_columns_match": True,
        "canonical_tuple_sha256": digest.hexdigest(), "samples": samples,
        "archive_sha256": hashlib.file_digest((ROOT / "logs.zip").open("rb"), "sha256").hexdigest(),
    }
    evidence = ROOT / "docs/evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / "database-verification.json").write_text(json.dumps(output, indent=2, default=str) + "\n")
    print(json.dumps(output, indent=2, default=str))


def integration():
    # Always create our own database. Never truncate the historical database.
    name = "hpc_test_" + uuid.uuid4().hex[:12]
    connection = connect()
    connection.autocommit = True
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
        child_env = dict(os.environ)
        parameters = connection.get_dsn_parameters()
        parameters.update(dbname=name, password=os.environ["POSTGRES_PASSWORD"])
        child_env["TEST_DATABASE_DSN"] = psycopg2.extensions.make_dsn(**parameters)
        result = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT, env=child_env)
    finally:
        with connection.cursor() as cursor:
            cursor.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(name)))
        connection.close()
    if result.returncode:
        raise SystemExit(result.returncode)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["init-env", "setup", "load", "verify", "integration"])
    args = parser.parse_args()
    environment()
    if args.command == "init-env":
        return init_env()
    if args.command == "integration":
        return integration()
    connection = connect()
    try:
        if args.command == "setup":
            setup(connection)
        elif args.command == "verify":
            verify(connection)
        elif args.command == "load":
            # Delegate to the loader CLI so summary preflight and failure exits apply.
            connection.close()
            return subprocess.run([sys.executable, "-m", "db.loader"], cwd=ROOT, env=dict(os.environ)).check_returncode()
    finally:
        connection.close()


if __name__ == "__main__":
    main()
