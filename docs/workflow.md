# Reproduce the historical cluster dashboard

Use Docker Engine with Compose on Linux, or Docker Desktop in Linux-container
mode on Windows. Python 3.13 is used in CI and the tooling container. No full
Linux VM is necessary for this application. A deployment VM needs Docker,
Compose, Git and enough space for images, raw logs, generated reports and the DB;
start with 2 CPUs and 8 GiB RAM. The laptop's 16 GiB is sufficient for the tested
local workflow. Keep ports bound to loopback; use an SSH tunnel for a remote VM.

## First setup — Linux terminal

Run inside the repository checkout. Install Python 3.13 with venv support using
your distribution's supported method if absent. Stop each step on errors.

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m scripts.project init-env
docker compose up -d db --wait
docker compose run --build --rm runner python -m scripts.project setup
docker compose run --rm runner python scripts/clean_logs.py --all
docker compose run --rm runner python -m scripts.project integration
docker compose run --rm runner python -m scripts.project load
docker compose run --rm runner python -m scripts.project verify
docker compose run --rm runner python -m scripts.analyse
docker compose up -d grafana
```

The runner profile is activated automatically when explicitly targeted.
Runner outputs are written into the checkout through its bind mount. A Linux
Docker installation may create root-owned output files; use the host venv for
commands instead if you need user-owned outputs (same commands, without the
`docker compose run --rm runner` prefix; use `.venv/bin/python`).

## First setup — Windows PowerShell

Open Docker Desktop first and run these commands from the repository folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m scripts.project init-env
docker --context desktop-linux compose up -d db --wait
.\.venv\Scripts\python.exe -m scripts.project setup
.\.venv\Scripts\python.exe scripts\clean_logs.py --all
.\.venv\Scripts\python.exe -m scripts.project integration
.\.venv\Scripts\python.exe -m scripts.project load
.\.venv\Scripts\python.exe -m scripts.project verify
.\.venv\Scripts\python.exe -m scripts.analyse
docker --context desktop-linux compose up -d grafana
.\.venv\Scripts\python.exe -m scripts.check_dashboard
```

Expected: healthy DB, 903,522 accepted rows, zero failed imports, all 12 columns
matching the cleaned CSV, and successful dashboard API checks. Integration tests
create a disposable DB; never point TEST_DATABASE_DSN at the historical DB.
The project helper generates secrets without displaying them and preserves
existing `.env` values. Keep `.env` and the persistent volumes; never commit it.
Do not use `docker compose down -v` on a database you want to retain.

## Open and use

Open <http://127.0.0.1:3000/d/switch-squad-hpc>. The default range covers the supplied
archive. Select an absolute range using the date picker. Choose 1 hour, 1 day or
1 week in **Bucket**, hover a series, and drag across it to zoom. An empty range
should show no chart samples and a snapshot count of zero.

The viewer is anonymous for a laptop demo, with a SELECT-only PostgreSQL role.
Grafana admin is `admin` with the generated GRAFANA_ADMIN_PASSWORD in local
`.env`. Provisioned dashboards are source-controlled; edit the generator and
run `python scripts/build_dashboard.py`, then restart Grafana. Source mounts are
read-only. Keep this demo on loopback; production authentication, TLS and remote
backup are deployment work beyond the verified local submission.

## Stop, restart and preserve

Use `docker compose stop` to stop; `docker compose up -d db grafana` to restart.
Both services have persistent named volumes. Back up the DB before changing
machines with `pg_dump` using the container's existing environment; preserve
the raw archive, code revision and companion quality reports alongside it.
Rebuilding the DB from preserved raw data is also supported by the commands above.

## Checks and optional material exports

`python -m pytest -q` runs unit tests; database tests skip without an explicit
test DSN. `python -m scripts.project integration` runs them in a fresh database.
`python -m scripts.check_dashboard` exercises all panel queries and empty range
handling through Grafana. Browser/material tooling is optional: install
`requirements-materials.txt` and follow submission/README.md.

The older setup/database documents record earlier verification; this guide is
the current end-to-end route. Do not treat a historical result as a current test.
