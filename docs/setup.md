# Development setup

## Purpose

This project processes historical PBS cluster snapshots to analyse
resource usage and develop an interactive dashboard.

## Tools

- Windows
- PowerShell
- Git
- Visual Studio Code
- Python 3.13.14

## Initial Python version choice

Python 3.13.14 is available on the initial development machine.
We use a separate virtual environment for project packages.
Package compatibility is checked by importing Pandas and running
pip check. The team will verify this setup on their own machines.

## Reproduce the environment

Open PowerShell inside the project folder.

Confirm the installed Python version:

```powershell
python --version
```

Create the environment:

```powershell
python -m venv .venv
```

Install the recorded packages:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Verify the installation:

```powershell
.\.venv\Scripts\python.exe -c "import pandas as pd; print('Pandas version:', pd.__version__)"
.\.venv\Scripts\python.exe -m pip check
```

## Team verification

Each teammate should report their Python version, Pandas version,
installation result, and any problems in Issue #1.

The .venv folder remains on each teammate's laptop.
Installed package versions are recorded in requirements.txt.