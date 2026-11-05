"""Regression tests for the PR #22 review findings (standard library only)."""

from contextlib import redirect_stdout
import csv
import importlib.util
import io
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "clean_logs.py"
SPEC = importlib.util.spec_from_file_location("pbs_cleaner_under_test", SCRIPT)
cleaner = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = cleaner
SPEC.loader.exec_module(cleaner)

BASE_METRICS = {
    "jobs_running": "60", "jobs_queued": "2", "nodes_running": "484",
    "nodes_offline": "17", "nodes_total": "1012",
    "nodes_running_percent": "47.83%", "cpu_used": "3960",
    "cpu_total": "24448", "cpu_percent": "16.20%",
}


def record(timestamp="2017-01-22 08:25", **changes):
    values = {**BASE_METRICS, **changes}
    return timestamp + ", " + ", ".join(f"{key}={value}" for key, value in values.items())


def run_records(lines=None, *, files=None):
    if files is None:
        files = {"logs/test.log": lines}
    with TemporaryDirectory(prefix="pbs_cleaning_test_") as directory:
        root = Path(directory)
        archive_path = root / "logs.zip"
        with ZipFile(archive_path, "w") as archive:
            for filename, records in files.items():
                archive.writestr(filename, "\n".join(records))
        original = archive_path.read_bytes()
        output = root / "output"
        with ZipFile(archive_path) as archive, redirect_stdout(io.StringIO()):
            cleaner.process_files(archive, sorted(files), output)
        if archive_path.read_bytes() != original:
            raise AssertionError("The raw ZIP must remain unchanged")
        summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
        tables = {}
        for name in (
            "snapshots.csv", "rejected_rows.csv", "duplicate_rows.csv",
            "conflicting_snapshots.csv", "quality_warnings.csv",
        ):
            with (output / name).open(encoding="utf-8", newline="") as stream:
                tables[name] = list(csv.DictReader(stream))
        return summary, tables


class CleaningRegressionTests(unittest.TestCase):
    def test_comma_and_space_formats(self):
        comma = record()
        space = comma.replace(", ", " ")
        for line in (comma, space):
            with self.subTest(line=line):
                parsed, date, _ = cleaner.parse_line(line)
                self.assertEqual(date, "2017-01-22")
                self.assertEqual(parsed["jobs_running"], 60)
                self.assertEqual(parsed["cpu_percent"], 16.2)

    def test_missing_required_fields_are_rejected(self):
        summary, tables = run_records(["2017-01-22 08:25, jobs_held=0"])
        self.assertEqual(summary["clean_rows"], 0)
        self.assertEqual(summary["rejected_rows"], 1)
        self.assertIn("jobs_running", tables["rejected_rows.csv"][0]["reason"])

    def test_optional_measurements_can_be_empty(self):
        parsed, _, warnings = cleaner.parse_line(record(
            nodes_running="0", nodes_offline="0", nodes_total="0",
            nodes_running_percent="", cpu_used="", cpu_total="", cpu_percent="",
        ))
        self.assertEqual(parsed["nodes_total"], 0)
        self.assertEqual(parsed["cpu_percent"], "")
        self.assertEqual(parsed["jobs_held"], "")
        self.assertIn("Total node count is zero", warnings)

    def test_rejected_metrics_do_not_lose_a_valid_date(self):
        summary, tables = run_records([
            record("2017-01-21 23:55"),
            record("2017-01-22 00:00", jobs_running="bad"),
            record("00:05"),
        ])
        self.assertEqual(summary["rejected_rows"], 1)
        self.assertEqual(
            [row["timestamp"] for row in tables["snapshots.csv"]],
            ["2017-01-21 23:55", "2017-01-22 00:05"],
        )

    def test_backwards_time_only_requires_a_new_explicit_date(self):
        summary, tables = run_records([
            record("2017-01-21 23:55"), record("00:00"), record("00:05"),
            record("2017-01-22 00:10"), record("00:15"),
        ])
        self.assertEqual(summary["rejected_rows"], 2)
        self.assertEqual(
            [row["timestamp"] for row in tables["snapshots.csv"]],
            ["2017-01-21 23:55", "2017-01-22 00:10", "2017-01-22 00:15"],
        )
        self.assertIn("moved backwards", tables["rejected_rows.csv"][0]["reason"])

    def test_a_b_b_is_one_conflicting_time_and_one_duplicate(self):
        a = record()
        b = record(jobs_running="61")
        summary, tables = run_records([a, b, b])
        self.assertEqual(summary["input_nonblank_rows"], 3)
        self.assertEqual(summary["clean_rows"], 0)
        self.assertEqual(summary["duplicate_rows"], 1)
        self.assertEqual(summary["conflicting_timestamps"], 1)
        self.assertEqual(summary["conflicting_variants"], 2)
        self.assertTrue(summary["row_accounting_ok"])
        self.assertEqual(tables["snapshots.csv"], [])
        conflicts = tables["conflicting_snapshots.csv"]
        self.assertEqual(
            {json.loads(row["record"])["jobs_running"] for row in conflicts}, {60, 61}
        )
        self.assertEqual({row["identical_occurrences"] for row in conflicts}, {"1", "2"})
        self.assertEqual(tables["duplicate_rows.csv"][0]["duplicate_of_line"], "2")

    def test_same_values_at_different_times_are_kept_and_sorted(self):
        summary, tables = run_records([record("2017-01-22 08:30"), record()])
        self.assertEqual(summary["clean_rows"], 2)
        self.assertEqual(summary["duplicate_rows"], 0)
        self.assertEqual(
            [row["timestamp"] for row in tables["snapshots.csv"]],
            ["2017-01-22 08:25", "2017-01-22 08:30"],
        )

    def test_conflict_counts_use_distinct_timestamps(self):
        summary, _ = run_records([
            record(), record(jobs_running="61"), record(jobs_running="62"),
            record(jobs_running="61"),
            record("2017-01-22 08:30"),
            record("2017-01-22 08:30", jobs_running="61"),
            record("2017-01-22 08:30", jobs_running="61"),
        ])
        self.assertEqual(summary["conflicting_timestamps"], 2)
        self.assertEqual(summary["conflicting_variants"], 5)
        self.assertEqual(summary["duplicate_rows"], 2)
        self.assertEqual(summary["input_nonblank_rows"], 7)

    def test_metric_order_and_numeric_format_do_not_hide_duplicates(self):
        parts = record(jobs_running="060", cpu_percent="16.200%").split(", ")
        reordered = parts[0] + ", " + ", ".join(reversed(parts[1:]))
        summary, _ = run_records([record(), reordered])
        self.assertEqual(summary["clean_rows"], 1)
        self.assertEqual(summary["duplicate_rows"], 1)

    def test_deduplication_spans_files(self):
        summary, tables = run_records(files={
            "logs/one.log": [record()], "logs/two.log": [record()],
        })
        self.assertEqual(summary["files_processed"], 2)
        self.assertEqual(summary["clean_rows"], 1)
        self.assertEqual(summary["duplicate_rows"], 1)
        self.assertEqual(tables["duplicate_rows.csv"][0]["duplicate_of_source"], "logs/one.log")


if __name__ == "__main__":
    unittest.main()
