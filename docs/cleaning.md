# HPC Log Cleaning Report

## Processing summary

- Files processed: 3169
- Nonblank input rows: 917919
- Blank lines: 0
- Clean rows: 904459
- Rejected rows: 1
- Identical duplicate rows: 12473
- Conflicting timestamps: 986
- Quality warnings: 201772

## Timestamp range

- First timestamp: 2017-01-22 08:25
- Last timestamp: 2025-10-03 15:10

## Cleaning rules

1. Read PBS log files from the supplied ZIP archive.
2. Support both historical log formats.
3. Require timestamp and core job and node measurements.
4. Treat optional measurements as missing when absent.
5. Convert integer and percentage measurements to numeric values.
6. Preserve CPU percentages above 100% and flag them.
7. Retain node-count inconsistencies and flag them.
8. Retain zero-node snapshots with missing percentages.
9. Infer time-only dates from the preceding dated record.
10. Reject records with invalid or missing required information.
11. Identify and record identical duplicates.
12. Preserve conflicting records for manual review.
13. Retain the first valid occurrence provisionally.
14. Sort clean snapshots chronologically.

## Important limitations

Time-only dates are inferred from the preceding dated record
within the same file. These inferred dates are flagged for review.

Conflicting snapshots are not silently discarded:
their original metric values are preserved in the conflict report.
The first valid record is retained provisionally in snapshots.csv.

The source timezone has not been established. No timezone
has been assigned to the timestamps.

Missing values remain empty; they are not replaced with zero.
Quality warnings do not automatically cause a record to be rejected.
