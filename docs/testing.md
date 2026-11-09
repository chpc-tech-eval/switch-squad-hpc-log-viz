# Cleaning Pipeline Tests

## Purpose

The tests check the cleaning rules using small generated ZIP files. They verify
the output records and quality reports without reading or changing the supplied
project dataset. Temporary test files are removed after each test.

This change keeps the 10 regression tests introduced with the cleaning pipeline
and adds 11 edge-case tests. The expected total at this revision is 21 tests;
some test methods also check several input values with subtests.

## Run locally

Open PowerShell inside the cloned project folder and run:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

The test suite uses Python's standard library. No extra test package is required.
The command should finish with `OK`. Read any failure before committing changes;
the failure identifies the test and the expected behaviour that was not met.

## Coverage

| Area | Behaviour checked |
|---|---|
| Input formats | Comma-separated and space-separated snapshots |
| Empty input | Empty logs and blank lines produce no invented snapshots |
| Missing or invalid data | Required fields, invalid integers, repeated fields and invalid percentages are rejected |
| Corrupt records | The original row and source location are preserved while later valid records continue processing |
| Optional measurements | Empty CSV cells remain distinct from recorded zero values |
| Timestamp context | A rejected metric does not lose a valid date; ambiguous backwards time-only records require a new explicit date |
| Out-of-order dated input | Accepted snapshots are sorted chronologically |
| Duplicates | Numeric formatting and field order do not hide repeats; comparison spans files |
| Conflicts | All distinct conflicting variants are quarantined; timestamps and variants are counted separately |
| Quality warnings | CPU percentages above 100 are preserved and flagged, following the schema |
| Schema changes | Unrecognised fields are rejected for review |
| Accounting | Mixed clean, rejected, duplicate and conflicting records account for every nonblank input once |
| Archive contents | The command reports an error when the ZIP contains no log files |

Regression cases are in `tests/test_clean_logs.py`. The additional cases are in
`tests/test_clean_logs_edge_cases.py`, which reuses the existing fixture helpers.

## Continuous integration

The workflow `.github/workflows/tests.yml` runs the same discovery command in
GitHub Actions on pushes and pull requests. It also supports a manual run.
It uses an Ubuntu runner with Python 3.13. The cleaner and its tests use the
standard library, so this workflow does not install the project's Pandas
dependencies.

The workflow is named **Cleaning pipeline tests** and its job is **Unit tests**.
Check that the run for the new commit succeeds before merging the pull request.
After merging, check the run on `main` as well.

A branch push associated with an open pull request can produce both a push run
and a pull-request run. Both use the same test command.

## Reporting results

In the pull request, record the local Python version, the number of tests run,
whether the result was `OK`, and the GitHub Actions run link. These unit tests
validate behaviour on generated cases. Full-archive processing results remain
documented separately in `docs/cleaning.md`.
