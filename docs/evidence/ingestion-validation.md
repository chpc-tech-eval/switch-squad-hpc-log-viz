# Ingestion validation — 16 November 2026

Executed on the project owner's Windows laptop with Python 3.13.14 and
Linux TimescaleDB containers through Docker Desktop. These are newly executed
checks, rather than inherited claims from the existing documentation.

| Check | Result |
|---|---|
| Original cleaning suite | 21 tests passed |
| Expanded unit suite | 41 passed, 2 database tests skipped, 13 subtests passed |
| Suite with disposable TimescaleDB | 43 passed, 13 subtests passed |
| Full archive input | 3,169 files; 917,919 nonblank rows |
| Accepted / extra duplicates / rejected | 903,522 / 12,489 / 1 |
| Conflicting timestamps / distinct variants | 937 / 1,907; all variants quarantined |
| Quality warning events | 201,772 |
| Input/output accounting | Passed |
| Initial database import | 903,522 inserted; zero failures |
| Full repeat import | Zero inserted; 903,522 identical duplicates; zero failures |
| Full ordered CSV/database comparison | All 903,522 rows and all 12 columns match |

The machine-readable comparison, sampled values and archive digest are in
`database-verification.json`. The schema retains naive timestamps and NULLs.
Integration tests create a new database and remove only that newly created
test database. They do not truncate the historical data.

Reproduce with `python scripts/clean_logs.py --all`,
`python -m scripts.project integration`, `python -m scripts.project load`,
and `python -m scripts.project verify` after following the setup guide.
