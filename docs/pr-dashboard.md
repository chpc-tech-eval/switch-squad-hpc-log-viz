Complete the historical-data query and Grafana workflow required by #9–11.

Add documented SQL for summary, hourly/daily/weekly peaks, weekday/hour patterns
and coverage gaps; a generated findings report; provisioned Grafana with date
filtering, hour/day/week buckets, job/node/CPU trends and coverage panels; a
SELECT-only datasource role; and a Linux tooling container plus Windows/Linux
instructions. Preserve missing values, conflicting-source quarantine and source
wall-clock times. Explicitly document metrics the aggregate dataset cannot supply.

Validation: every one of 903,522 database rows matches all 12 canonical CSV
fields, including from the Linux runner. Real Grafana API checks exercise 12
query panels at all three bucket settings and an empty range. Chrome screenshots
and browser results are included. Actual measurements and query results are in
docs/evidence/. Ingestion integration tests also run on Linux.

Dependency and merge order: #27, then #28, then this PR. This branch targets
completion/ingestion so its diff contains only the next cohesive change.
Reviewers perform merges. Related: #9, #10, #11; no automatic issue closures.

Limits: source timezone and CPU collection semantics are unconfirmed. Queue
counts do not establish waiting time or throughput. No node IDs or memory
measurements exist. Grafana is a loopback-only local demo; remote hosting and
organiser acceptance of metric substitutions are unverified.
