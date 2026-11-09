# Canonical Snapshot Schema

## Purpose and scope

This document defines version 1 of the logical schema for cleaned cluster
snapshots. It documents the column names and validation rules currently
implemented in `scripts/clean_logs.py`.

The logical table or measurement name is `cluster_snapshots`. Each row
represents one accepted snapshot of the supplied cluster. The timestamp
identifies a snapshot within this single-cluster dataset. These are aggregate
cluster measurements, not individual job or node records.

The canonical intermediate file is `data/cleaned/snapshots.csv`.
Database-specific table definitions and integer storage widths will be mapped
when the time-series database is selected. This document does not create a
database table.

## Column definitions

The table below follows the CSV column order. Required means that an absent or
empty value causes the source row to be rejected. Optional means that an absent
or empty value is represented by an empty CSV cell and treated as a logical
null value when loaded for analysis or storage.

| Column | Logical type | Required | Meaning |
|---|---|---|---|
| `timestamp` | Date and time, timezone unconfirmed | Yes | Snapshot time, written as `YYYY-MM-DD HH:MM` |
| `jobs_running` | Nonnegative integer | Yes | Reported number of running jobs |
| `jobs_queued` | Nonnegative integer | Yes | Reported number of queued jobs |
| `jobs_held` | Nullable nonnegative integer | No | Reported number of held jobs, when supplied |
| `jobs_exiting` | Nullable nonnegative integer | No | Reported number of exiting jobs, when supplied |
| `nodes_running` | Nonnegative integer | Yes | Reported number of running nodes |
| `nodes_offline` | Nonnegative integer | Yes | Reported number of offline nodes |
| `nodes_total` | Nonnegative integer | Yes | Reported total node count; zero is retained with a warning |
| `nodes_running_percent` | Nullable nonnegative finite number | No | Reported running-node percentage |
| `cpu_used` | Nullable nonnegative integer | No | Reported CPU-use count; collection meaning and counting unit require confirmation |
| `cpu_total` | Nullable nonnegative integer | No | Reported total CPU count; counting unit requires confirmation |
| `cpu_percent` | Nullable nonnegative finite number | No | Reported CPU percentage; collection method requires confirmation |

The current cleaner uses Python integers and floats. Before choosing fixed-width
database integer types, the loader must check that values fit those types.

## Timestamp rules

- The canonical CSV format is `YYYY-MM-DD HH:MM`, at minute precision.
- The source timezone has not been established. Preserve the recorded wall-clock
  values without adding an offset or claiming that they are UTC.
- Confirm the source timezone with the dataset provider before converting these
  values to UTC for a database that requires it.
- A time-only source record can use an established explicit date from the same
  file when its inferred timestamp does not move backwards.
- A valid explicit timestamp updates date context even when that row's metrics
  are subsequently rejected.
- A backwards time-only value is ambiguous: it may be a rollover or an out-of-order
  record. Reject it and clear the date context until a new explicit date appears.
- Accepted inferred dates are recorded as warning events in the companion
  quality report. No next-day rollover is guessed automatically.

## Numeric and missing-value rules

- Nonempty count measurements must parse as nonnegative whole numbers.
- Nonempty percentage measurements must parse as finite, nonnegative numbers.
- Remove a trailing percent sign when parsing a percentage. The value `16.20%`
  becomes the numeric value `16.2`, meaning 16.2 percent, not 0.162.
- Keep optional missing measurements empty. Do not replace them with zero.
  A recorded zero and an unavailable measurement have different meanings.
- Do not clamp reported percentages to 100. The current cleaner retains CPU
  percentages above 100 and records a warning for review.
- The current cleaner warns about zero total nodes, running plus offline nodes
  exceeding total nodes, and CPU use exceeding total CPU. These warnings do not
  automatically reject a record.
- Warning counts represent events. Several warnings can belong to one source
  row, and missing optional historical measurements can generate warnings.
- Unknown field names are rejected for review by the current cleaner. Adding a
  new canonical field requires a corresponding schema, cleaner and test update.

CPU counting units and the meaning of the reported CPU percentage remain
unconfirmed. This schema does not establish that the percentage measures actual
hardware busy time or that CPU counts measure physical cores.

## Uniqueness and duplicate handling

The cleaned CSV contains at most one row for a timestamp in this dataset.

- Same timestamp and identical normalised measurements: retain one record and
  record each additional occurrence in `duplicate_rows.csv`.
- Same timestamp and different normalised measurements: preserve every distinct
  variant in `conflicting_snapshots.csv`. Exclude that timestamp from the cleaned
  CSV until the conflict is resolved.
- Identical measurements at different timestamps remain separate snapshots.
- Sort accepted clean snapshots chronologically.
- Do not create artificial snapshot records to fill gaps.

Normalised comparison includes all 12 canonical columns. For example, numeric
percentage strings with different decimal formatting can represent the same
value after parsing.

## Companion quality records

These files support review and traceability and are separate from the canonical
snapshot table. Source references are retained in these companion reports.

| File | Purpose |
|---|---|
| `rejected_rows.csv` | Source location, original line and reason for rejection |
| `duplicate_rows.csv` | Additional identical occurrences and their representative source references |
| `conflicting_snapshots.csv` | Each distinct conflicting variant, its source and its identical occurrence count |
| `quality_warnings.csv` | Warning events linked to source rows and timestamps |
| `summary.json` | Processing totals and row-accounting result |

The row-accounting rule is:

`nonblank input rows = clean rows + rejected rows + extra identical duplicates + distinct conflicting variants`

The number of conflicting timestamps is separate from the number of conflicting
variants. One timestamp may have more than two variants.

## Fields absent from the current cleaned output

The current cleaned schema supplies no individual `job_id`, `node_id`, job-state
history, queue name, user identity or memory-usage field. Do not manufacture
these values or derive individual job waiting times from the aggregate counts.
The `jobs_running`, `jobs_queued`, `jobs_held` and `jobs_exiting` columns describe
aggregate counts in those states.

## Example canonical CSV

This example uses the previously inspected `2017-01-22 08:25` snapshot.
The two empty cells represent unavailable held and exiting job counts.

```csv
timestamp,jobs_running,jobs_queued,jobs_held,jobs_exiting,nodes_running,nodes_offline,nodes_total,nodes_running_percent,cpu_used,cpu_total,cpu_percent
2017-01-22 08:25,60,2,,,484,17,1012,47.83,3960,24448,16.2
```

## Related project files

- `scripts/clean_logs.py`: parsing, validation, duplicate handling and CSV output.
- `tests/test_clean_logs.py`: regression checks for the cleaning rules.
- `docs/cleaning.md`: the recorded full-archive cleaning results and limitations.
- `docs/eda.md`: initial exploration of a sample file.
- `docs/dataset_inventory.md`: dataset inventory documentation.
