"""Additional edge cases for Issue #6, using small generated log files."""

from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from zipfile import ZipFile

from test_clean_logs import cleaner, record, run_records


class CleaningEdgeCaseTests(unittest.TestCase):
    def test_empty_log_produces_empty_output_without_invented_rows(self):
        summary, tables = run_records([])
        self.assertEqual(summary["files_processed"], 1)
        self.assertEqual(summary["input_nonblank_rows"], 0)
        self.assertEqual(summary["clean_rows"], 0)
        self.assertIsNone(summary["first_timestamp"])
        self.assertIsNone(summary["last_timestamp"])
        self.assertEqual(tables["snapshots.csv"], [])
        self.assertTrue(summary["row_accounting_ok"])

    def test_blank_lines_are_ignored_and_counted(self):
        summary, tables = run_records(["", " ", "\t", record()])
        self.assertEqual(summary["blank_lines"], 3)
        self.assertEqual(summary["input_nonblank_rows"], 1)
        self.assertEqual(len(tables["snapshots.csv"]), 1)

    def test_corrupt_line_is_preserved_and_later_records_are_processed(self):
        corrupt = "this is not a valid PBS snapshot"
        summary, tables = run_records([record(), corrupt, record("2017-01-22 08:30")])
        self.assertEqual(summary["clean_rows"], 2)
        self.assertEqual(summary["rejected_rows"], 1)
        rejected = tables["rejected_rows.csv"][0]
        self.assertEqual(rejected["original_line"], corrupt)
        self.assertEqual(rejected["line_number"], "2")
        self.assertTrue(rejected["reason"])

    def test_repeated_metric_name_is_rejected(self):
        summary, tables = run_records([record() + ", jobs_running=61"])
        self.assertEqual(summary["clean_rows"], 0)
        self.assertEqual(summary["rejected_rows"], 1)
        self.assertIn("repeated field", tables["rejected_rows.csv"][0]["reason"])

    def test_invalid_required_integer_is_rejected(self):
        for value in ("-1", "1.5", "not-a-number"):
            with self.subTest(value=value):
                summary, tables = run_records([record(jobs_running=value)])
                self.assertEqual(summary["clean_rows"], 0)
                self.assertEqual(summary["rejected_rows"], 1)
                self.assertIn("jobs_running", tables["rejected_rows.csv"][0]["reason"])

    def test_nonfinite_negative_or_invalid_percentages_are_rejected(self):
        for field in ("nodes_running_percent", "cpu_percent"):
            for value in ("NaN%", "inf%", "-0.5%", "not-a-number"):
                with self.subTest(field=field, value=value):
                    summary, tables = run_records([record(**{field: value})])
                    self.assertEqual(summary["clean_rows"], 0)
                    self.assertEqual(summary["rejected_rows"], 1)
                    self.assertIn(field, tables["rejected_rows.csv"][0]["reason"])

    def test_optional_csv_blanks_remain_different_from_recorded_zero(self):
        summary, tables = run_records([record(
            jobs_held="0", nodes_running_percent="", cpu_used="",
            cpu_total="", cpu_percent="",
        )])
        self.assertEqual(summary["clean_rows"], 1)
        exported = tables["snapshots.csv"][0]
        self.assertEqual(exported["jobs_held"], "0")
        self.assertEqual(exported["jobs_running"], "60")
        for field in ("jobs_exiting", "nodes_running_percent", "cpu_used", "cpu_total", "cpu_percent"):
            self.assertEqual(exported[field], "")

    def test_cpu_percentage_above_100_is_preserved_and_warned(self):
        summary, tables = run_records([record(cpu_percent="125%")])
        self.assertEqual(summary["clean_rows"], 1)
        self.assertEqual(summary["rejected_rows"], 0)
        self.assertEqual(float(tables["snapshots.csv"][0]["cpu_percent"]), 125.0)
        self.assertTrue(any(
            warning["warning"].startswith("cpu_percent exceeds 100%")
            for warning in tables["quality_warnings.csv"]
        ))

    def test_unrecognised_field_is_rejected_for_schema_review(self):
        summary, tables = run_records([record() + ", mem_usage=42"])
        self.assertEqual(summary["clean_rows"], 0)
        self.assertEqual(summary["rejected_rows"], 1)
        self.assertIn("mem_usage", tables["rejected_rows.csv"][0]["reason"])

    def test_mixed_rows_account_for_every_nonblank_input_once(self):
        summary, tables = run_records([
            record(), "", "corrupt row", record(),
            record("2017-01-22 08:30"),
            record("2017-01-22 08:30", jobs_running="61"),
            record("2017-01-22 08:35"),
        ])
        self.assertEqual(summary["input_nonblank_rows"], 6)
        self.assertEqual(summary["blank_lines"], 1)
        self.assertEqual(summary["clean_rows"], 2)
        self.assertEqual(summary["rejected_rows"], 1)
        self.assertEqual(summary["duplicate_rows"], 1)
        self.assertEqual(summary["conflicting_timestamps"], 1)
        self.assertEqual(summary["conflicting_variants"], 2)
        self.assertTrue(summary["row_accounting_ok"])
        self.assertEqual(
            [row["timestamp"] for row in tables["snapshots.csv"]],
            ["2017-01-22 08:25", "2017-01-22 08:35"],
        )

    def test_archive_without_logs_reports_an_error(self):
        with TemporaryDirectory(prefix="pbs_empty_archive_") as directory:
            root = Path(directory)
            archive_path = root / "logs.zip"
            with ZipFile(archive_path, "w") as archive:
                archive.writestr("readme.txt", "No log files in this fixture")
            with (
                patch.object(cleaner, "ROOT", root),
                patch.object(cleaner, "ARCHIVE", archive_path),
                patch.object(sys, "argv", ["clean_logs.py", "--all"]),
            ):
                with self.assertRaisesRegex(FileNotFoundError, r"No \.log files"):
                    cleaner.main()
            self.assertFalse((root / "data").exists())


if __name__ == "__main__":
    unittest.main()
