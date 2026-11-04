# Initial Exploratory Data Analysis

## Purpose

Explore a sample of the supplied HPC cluster snapshots using Pandas,
summarise the available metrics, and identify fields for the dashboard.

## Sample and method

- Archive: `logs.zip`
- Sample file: `logs/2017-01-22.log`
- Analysis script: `scripts/eda.py`
- Pandas version: `3.0.6`
- Records loaded: 187
- Fields: one timestamp and nine numeric metrics

The script reads the sample directly from the archive, parses timestamps,
and converts metric values into numbers. Percentage values remain on a
0–100 scale: for example, `16.20%` becomes `16.20`.

## Time coverage

- First timestamp: 2017-01-22 08:25
- Last timestamp: 2017-01-22 23:55
- All 186 gaps between distinct, chronologically sorted timestamps
  were five minutes.
- No gaps were detected within this observed window.
- The sample covers part of one day.
- The timestamp timezone is not confirmed.

These results describe this sample file, not the entire archive.

## Numeric summary

Every metric had 187 valid numeric values. Means are rounded to
two decimal places.

| Field | Minimum | Maximum | Mean |
|---|---:|---:|---:|
| jobs_running | 52 | 117 | 80.80 |
| jobs_queued | 1 | 15 | 5.30 |
| nodes_running | 472 | 665 | 536.41 |
| nodes_offline | 17 | 17 | 17.00 |
| nodes_total | 1012 | 1012 | 1012.00 |
| nodes_running_percent | 46.64% | 65.71% | 53.00% |
| cpu_used | 3697 | 8366 | 5252.17 |
| cpu_total | 24448 | 24448 | 24448.00 |
| cpu_percent | 15.12% | 34.22% | 21.48% |

The mean is the arithmetic average across the recorded snapshots.
An average job or node count can therefore contain a fraction.

## Initial findings

- Running jobs ranged from 52 to 117, averaging approximately 80.80.
- Queued jobs ranged from 1 to 15. A queue was present in every
  recorded snapshot.
- Running nodes ranged from 472 to 665.
- The reported offline node count remained at 17.
- The reported total node and CPU counts remained constant.
- The reported CPU percentage ranged from 15.12% to 34.22%,
  averaging approximately 21.48%.

These observations do not establish the cause of changes in workload
or resource usage.

## Data-quality checks

| Check | Result |
|---|---:|
| Blank lines | 0 |
| Malformed rows detected by the parser | 0 |
| Unparseable timestamps | 0 |
| Repeated timestamps | 0 |
| Missing or invalid numeric values across the nine metrics | 0 |

The checks did not identify these problems in the selected sample.
This does not establish the quality of all files in the archive.

## Candidate dashboard fields

| Purpose | Available fields |
|---|---|
| Time axis and date filtering | timestamp |
| Running and queued workload | jobs_running, jobs_queued |
| Node activity and availability | nodes_running, nodes_offline, nodes_total |
| Reported running-node percentage | nodes_running_percent |
| Reported CPU metrics | cpu_used, cpu_total, cpu_percent |

The job fields are aggregate counts. This sample does not contain
individual job IDs, individual job-state histories, or node IDs.

## Limitations

- Findings cover one sample file and cannot establish long-term trends.
- The sample mean is not a complete 24-hour daily average.
- Snapshot counts cannot establish the number of unique jobs completed
  or individual job waiting times.
- The collector's CPU counting units and measurement method still
  require confirmation. The reported CPU percentage must not yet be
  treated as a confirmed measurement of hardware busy time.
- Full-archive coverage and data-quality findings belong in the
  dataset inventory.

## Reproduce the analysis

From the repository folder in PowerShell:

```powershell
.\.venv\Scripts\python.exe .\scripts\eda.py
```
