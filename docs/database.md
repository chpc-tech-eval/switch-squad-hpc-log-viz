# Local time-series database

This guide covers the local TimescaleDB setup for Issue #7. The database stores
cleaned cluster snapshots using the canonical schema from [schema.md](schema.md).
Historical CSV loading is covered by Issue #8.

## Deployment and connection

The database runs in a Linux container through Docker Desktop on a Windows
laptop. The Compose service is named `db`.

| Setting | Value |
|---|---|
| Database | `hpc_logs` |
| Username | `hpc_admin` |
| Host from Windows | `127.0.0.1` |
| Port from Windows | `5433` |
| Port inside the container | `5432` |
| Password | `POSTGRES_PASSWORD` in the local `.env` file |
| Snapshot table | `public.cluster_snapshots` |
| Persistent Docker volume | `switch-squad-hpc_pgdata` |
| Configured resource limits | 2 CPUs and 2 GiB memory |

`compose.yaml` pins the verified image by digest:

```text
timescale/timescaledb@sha256:b56a3f51991df1f79d0c1a0841cad5c5fa8058fdd6a3ee6886394a6d4c174538
```

This image was verified with PostgreSQL **17.11** and TimescaleDB **2.31.0**.
The host port is bound to the laptop's loopback address.
If another service is added to this Compose project, it can connect using the
service name `db` and port `5432`.

## Prerequisites and working folder

- Install Docker Desktop with its WSL 2 backend and Linux containers enabled.
- Keep Docker Desktop running while using the database.
- Have Git and a checkout of this repository containing `compose.yaml` and
  `db/schema.sql`.
- Run the commands below in Windows PowerShell, one at a time. Stop on errors.

To get a new checkout after these files are merged into `main`:

```powershell
git clone https://github.com/chpc-tech-eval/switch-squad-hpc-log-viz.git
Set-Location .\switch-squad-hpc-log-viz
```

For an existing checkout, open its folder in File Explorer, type `powershell`
in the address bar and press Enter. Confirm the working folder:

```powershell
git status
Test-Path .\compose.yaml
```

The second command must return `True`. Check Docker is available:

```powershell
docker version
docker compose version
```

## First-time setup

Generate a local password file. This block preserves an existing `.env` file:

```powershell
if (Test-Path .env) {
    Write-Host ".env already exists; keeping it."
} else {
    Set-Content -Path .env -Encoding ascii -Value ("POSTGRES_PASSWORD=" + [guid]::NewGuid().ToString("N"))
}
```

Keep this file when reusing the existing database. Each teammate should create
their own local password. The committed `.gitignore` excludes `.env`.
Confirm this before committing project files:

```powershell
git check-ignore .env
```

Expected output: `.env`. Keep the password and `.env` contents private.

Validate the configuration without displaying resolved environment values:

```powershell
docker compose config --quiet
```

No output indicates successful validation. Start the database:

```powershell
docker compose up -d --wait --wait-timeout 180
docker compose ps
```

The service should show `healthy`. The first startup downloads the pinned image.
Apply the schema file explicitly:

```powershell
docker compose exec -T db psql -h 127.0.0.1 -U hpc_admin -d hpc_logs -v ON_ERROR_STOP=1 -f /project-db/schema.sql
```

The `db` folder is mounted read-only at `/project-db` in the container.
Startup alone does not run this project schema file. Run it for a fresh database;
reapplying the same file is safe for the existing matching schema.
The included `psql` client uses the password supplied through the container's
`PGPASSWORD` environment variable, so a Windows PostgreSQL installation is not
needed for these commands.

## Table structure and validation

`db/schema.sql` defines the 12 columns in the same order as the canonical cleaned
CSV. Each accepted row represents one cluster snapshot.

| Column | PostgreSQL type | Required |
|---|---|---|
| `timestamp` | `TIMESTAMP WITHOUT TIME ZONE` | Yes; primary key |
| `jobs_running` | `BIGINT` | Yes |
| `jobs_queued` | `BIGINT` | Yes |
| `jobs_held` | `BIGINT` | No |
| `jobs_exiting` | `BIGINT` | No |
| `nodes_running` | `BIGINT` | Yes |
| `nodes_offline` | `BIGINT` | Yes |
| `nodes_total` | `BIGINT` | Yes |
| `nodes_running_percent` | `DOUBLE PRECISION` | No |
| `cpu_used` | `BIGINT` | No |
| `cpu_total` | `BIGINT` | No |
| `cpu_percent` | `DOUBLE PRECISION` | No |

Counts must be nonnegative. The loader must validate that integer values fit
`BIGINT`: the allowed nonnegative range is 0 through 9223372036854775807.
Optional missing values are SQL `NULL`; a recorded zero remains zero.
Percentages must be finite and nonnegative. They use percentage points, so
`16.2` means 16.2 percent.

The database preserves the canonical cleaner's rules: percentages above 100
are allowed, zero total nodes are allowed, and cross-counter inconsistencies
are retained for review through the cleaning quality reports. The database
does not enforce additional relationships such as `cpu_used <= cpu_total`.
CPU counting units and the meaning of the reported CPU percentage remain
unconfirmed; see [schema.md](schema.md).

The timestamp primary key enforces at most one accepted snapshot per timestamp.
Conflicting source timestamps must be resolved or quarantined by the cleaning
workflow before loading.

## Timestamp decision

The source timezone is unconfirmed. `TIMESTAMP WITHOUT TIME ZONE` deliberately
preserves the recorded wall-clock values without declaring them to be UTC.

TimescaleDB recommends `TIMESTAMPTZ` and emits an advisory warning when this
hypertable is created. The warning was observed during verification; creation
completed and committed successfully.

Confirm the source timezone with the dataset provider before converting these
values or interpreting them as UTC in dashboards. Any later migration to
`TIMESTAMPTZ` must explicitly use the confirmed source timezone.

## Retention and storage

Retain all historical snapshots. No automatic retention or deletion policy is
configured by this setup. A short rolling retention window would discard the
historical dataset needed for this project.

The hypertable uses **30-day chunks**. This controls how TimescaleDB partitions
the records; it does not set an expiry period.

The named Docker volume `switch-squad-hpc_pgdata` is mounted at
`/var/lib/postgresql/data`. It stores the database independently of the container
and survives `docker compose down` followed by `docker compose up`.

## Routine operation

Start the database or recreate its container while reusing the volume:

```powershell
docker compose up -d --wait --wait-timeout 180
```

Stop the database:

```powershell
docker compose stop
```

Remove the container and project network while keeping the named volume:

```powershell
docker compose down
```

Do not add `-v` or `--volumes` when preserving data: those options remove the
named database volume. Keep the existing `.env` credentials when reusing it.

## Verification commands

Check the installed versions:

```powershell
docker compose exec -T db psql -h 127.0.0.1 -U hpc_admin -d hpc_logs -c "SELECT current_database() AS database_name, current_setting('server_version') AS postgres_version, extversion AS timescaledb_version FROM pg_extension WHERE extname = 'timescaledb';"
```

Inspect the columns and constraints:

```powershell
docker compose exec -T db psql -h 127.0.0.1 -U hpc_admin -d hpc_logs -c "\d public.cluster_snapshots"
```

Check the hypertable and row count:

```powershell
docker compose exec -T db psql -h 127.0.0.1 -U hpc_admin -d hpc_logs -c "SELECT hypertable_name FROM timescaledb_information.hypertables WHERE hypertable_schema = 'public'; SELECT COUNT(*) AS rows_loaded FROM public.cluster_snapshots;"
```

Before the Issue #8 import, the snapshot row count should be **0**. After import,
compare it with the accepted input records instead.

Check the Windows host port:

```powershell
Test-NetConnection -ComputerName 127.0.0.1 -Port 5433 -InformationLevel Quiet
```

Expected output: `True`.

### Persistence check

Use a separate test table to verify data survives removing and recreating the
container. Run each command separately and stop on errors:

```powershell
docker compose exec -T db psql -h 127.0.0.1 -U hpc_admin -d hpc_logs -v ON_ERROR_STOP=1 -c "BEGIN; CREATE TABLE public.issue7_persistence_probe (marker TEXT PRIMARY KEY); INSERT INTO public.issue7_persistence_probe (marker) VALUES ('issue7-storage-ok'); COMMIT;"
docker compose down
docker compose up -d --wait --wait-timeout 180
docker compose exec -T db psql -h 127.0.0.1 -U hpc_admin -d hpc_logs -v ON_ERROR_STOP=1 -c "SELECT marker FROM public.issue7_persistence_probe; SELECT COUNT(*) AS rows_loaded FROM public.cluster_snapshots;"
```

The marker must still be `issue7-storage-ok`. After confirming it, remove only
the test table:

```powershell
docker compose exec -T db psql -h 127.0.0.1 -U hpc_admin -d hpc_logs -v ON_ERROR_STOP=1 -c "DROP TABLE public.issue7_persistence_probe;"
```

## Results recorded on 2026-11-09

Verified on the project owner's Windows 11 Home x64 laptop, using Docker
Desktop 4.98.0, Docker Engine 29.9.2 and Docker Compose 5.6.1.

| Check | Observed result |
|---|---|
| `.env` ignored by Git | `.env` printed by `git check-ignore` |
| Compose validation | Passed with no output |
| Database container | Healthy |
| PostgreSQL | 17.11 |
| TimescaleDB extension | 2.31.0 |
| Table columns and constraints | All 12 canonical columns present |
| Hypertable | `cluster_snapshots` |
| Windows host TCP port | Reachable: `True` |
| Initial snapshot rows | 0 |
| Container recreated using the pinned image | Healthy |
| Test marker after recreation | `issue7-storage-ok` |
| Snapshot rows after recreation | 0 |
| Test-table cleanup | `DROP TABLE` completed |

The database is ready for the historical-data loader in Issue #8.

## References

- [Official TimescaleDB Docker image](https://github.com/timescale/timescaledb-docker/blob/main/README.md)
- [Docker Compose shutdown and volume options](https://docs.docker.com/reference/cli/docker/compose/down/)
- [PostgreSQL 17 date and time types](https://www.postgresql.org/docs/17/datatype-datetime.html)
