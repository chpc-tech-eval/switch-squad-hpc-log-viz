# Switch Squad HPC Log Visualization

This project processes historical PBS cluster snapshots to analyse
resource usage over time and develop an interactive dashboard.

## Run the completed workflow

Follow [the Linux and Windows walkthrough](docs/workflow.md) to clean the archive,
load TimescaleDB, verify every stored value, and open the provisioned Grafana
dashboard at <http://127.0.0.1:3000/d/switch-squad-hpc>.

The verified archive contains **903,522 accepted cluster snapshots**, from
January 2017 to October 2025. These are aggregate historical observations,
not individual job histories. See [requirements and metric limits](docs/requirements.md),
[observed findings](docs/analysis.md), and [validation evidence](docs/evidence/).

## Development setup

Follow the instructions in [docs/setup.md](docs/setup.md).

For database setup, see [docs/database.md](docs/database.md).

Run `python -m pytest -q` for unit tests and
`python -m scripts.project integration` for isolated real-database tests.
The latter creates its own disposable database and preserves historical data.

Submission poster, journal, slides, screenshots, demo guide and checklist are
in [submission/](submission/README.md). Review the checklist before submitting.

## Project files

- docs/: project documentation.
- requirements.txt: Python packages and their versions.
- logs.zip: supplied historical dataset.
