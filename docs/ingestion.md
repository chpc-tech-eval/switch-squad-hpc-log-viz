# Reliable snapshot ingestion

Run the canonical cleaner first, then `python -m db.loader`. The CLI checks the
CSV header and summary row count before connecting. Set POSTGRES_PASSWORD and
optionally PGHOST, PGPORT, PGUSER and PGDATABASE in the process environment.
Never put a password on the command line. Docker orchestration follows in the
dashboard change.

The loader retains Jurry's batched psycopg2 implementation from PR #27. It now
requires all mandatory fields, validates the BIGINT range, rejects malformed
row widths, and compares every existing measurement before accepting a repeat.
Identical snapshots are counted as skipped duplicates. Differing snapshots are
reported as failures and never overwrite stored values. Optional empty values
remain SQL NULL; zero and reported percentages above 100 remain unchanged.

Each batch commits independently. A data or conflict error rolls back that
batch, then retries its rows in individual transactions to identify failures.
Successful earlier batches remain committed if connectivity subsequently fails.
Rerunning is safe because identical rows are skipped. A failure exit means the
import needs review, even if some valid rows were committed. The canonical
cleaner quarantines conflicting source timestamps before ingestion; when given
a hand-edited CSV with new conflicting timestamps, the first valid row can be
stored and later differing rows are rejected.

`data/cleaned/ingestion_errors.csv` is replaced on each run and reports CSV row,
timestamp, error type and reason. Archive it before rerunning if needed. CLI
connection errors omit connection details to avoid printing credentials.

Validation: `python -m pytest` runs unit tests. Set TEST_DATABASE_DSN only to a
**disposable test database**, then rerun to include real TimescaleDB tests.
Those tests truncate cluster_snapshots in that test database. They exercise
NULLs, repeat import, conflicting values and transaction rollback/recovery.
CI supplies an isolated TimescaleDB service and never uses laptop credentials.
