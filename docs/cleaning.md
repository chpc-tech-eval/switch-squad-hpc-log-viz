# HPC Log Cleaning Report

## Processing summary

- Files processed: 3169
- Nonblank input rows: 917919
- Blank lines: 0
- Clean rows: 903522
- Rejected rows: 1
- Identical duplicate rows: 12489
- Conflicting timestamps: 937
- Conflicting variants quarantined: 1907
- Quality warning events: 201772
- Input/output row accounting passed: True

## Timestamp range of clean snapshots

- First timestamp: 2017-01-22 08:25
- Last timestamp: 2025-10-03 15:10

## Cleaning rules

1. Read PBS log files from the supplied ZIP archive.
2. Support both historical log formats.
3. Require a valid timestamp and nonempty jobs_running, jobs_queued,
   nodes_running, nodes_offline and nodes_total measurements.
4. Treat optional measurements as missing when absent.
5. Convert integer and percentage measurements to numeric values.
6. Preserve CPU percentages above 100% and flag them.
7. Retain node-count inconsistencies and flag them.
8. Retain zero-node snapshots with missing percentages.
9. Infer time-only dates only from an established explicit date with
   nondecreasing times. A valid dated timestamp updates date context
   even when that record's metrics are rejected.
10. Reject records with invalid or missing required information.
11. Identify and record identical duplicates.
12. Count distinct conflicting timestamps separately from their variants.
13. Quarantine every distinct variant at a conflicting timestamp;
    exclude that timestamp from snapshots.csv until resolved.
14. Sort clean snapshots chronologically.
15. Verify that nonblank input rows equal clean rows plus rejected rows
    plus extra identical duplicates plus distinct conflicting variants.

## Important limitations

Time-only dates use explicit date context within the same file.
Inferred dates are flagged for review. Backwards time-only values,
including ambiguous midnight rollovers, are rejected and clear the
date context. Following time-only records require a new explicit date.
No next-day rollover is guessed automatically.

Every distinct conflicting snapshot is preserved in the conflict report,
with source references and its number of identical occurrences.
Extra identical occurrences are listed separately in duplicate_rows.csv.
No unresolved conflicting timestamp appears in snapshots.csv.

The source timezone has not been established. No timezone
has been assigned to the timestamps.

Missing values remain empty; they are not replaced with zero.
Missing required measurements cause rejection; optional measurements
may be empty. The required-field list must agree with the schema in #5.
Quality warnings are individual events, not counts of distinct bad rows;
missing optional historical measurements also contribute warning events.
Warnings do not automatically cause a record to be rejected.
