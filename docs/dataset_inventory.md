# Historical HPC Snapshot Dataset Inventory

## Source and access

- **Repository location:** `logs/*.log`
- **Access method:** Read the plain-text log files from the local repository checkout.
- **Archive:** `logs.zip` is also present in the repository root.
- **Inspection script:** `scripts/inventory.py`
- **Machine-readable results:** `docs/inventory_results.json`

## Dataset structure

- **Log files:** 3169
- **Non-empty files:** 3165
- **Empty files:** 4
- **Total records parsed with valid timestamps:** 917629
- **First valid timestamp:** 2017-01-22 08:25
- **Last valid timestamp:** 2025-10-03 15:10
- **Expected snapshot interval:** 5 minutes
- **Expected records in a complete 24-hour day:** 288

Each non-empty log record is expected to contain a timestamp in
`YYYY-MM-DD HH:MM` format followed by comma-separated `key=value` metrics.

Expected metrics:

- `cpu_percent`
- `cpu_total`
- `cpu_used`
- `jobs_exiting`
- `jobs_held`
- `jobs_queued`
- `jobs_running`
- `nodes_offline`
- `nodes_running`
- `nodes_running_percent`
- `nodes_total`

## Data-quality checks

The inventory script checks blank or malformed records, missing fields,
empty values, unexpected fields, non-numeric metric values, duplicate lines,
duplicate timestamps, timestamp gaps, intervals shorter than five minutes,
and daily files whose line counts differ from 288.

| Check | Count |
|---|---:|
| Empty files | 4 |
| Files with line counts other than 288 | 226 |
| Malformed lines | 290 |
| Lines missing expected fields | 41623 |
| Empty metric values | 36652 |
| Duplicate timestamps | 13458 |
| Duplicate lines | 12441 |
| Timestamp gaps over five minutes | 1213 |
| Intervals shorter than five minutes | 14396 |
| Non-numeric metric values | 0 |
| Records with unexpected fields | 0 |

## Interpretation and limitations

A complete day sampled every five minutes should contain 288 records.
Files with different counts are candidates for incomplete days, missing
snapshots, extra records, or irregular collection. The count alone does not
prove which explanation applies; timestamp checks provide additional evidence.

The inventory describes the data as found and does not modify the source logs.
Review individual file details in `inventory_results.json` when investigating
specific anomalies.
