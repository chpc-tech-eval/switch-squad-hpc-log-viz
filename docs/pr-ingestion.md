Preserve PR #27's loader while making historical ingestion verifiable and safe to repeat.

Changes: required-field and BIGINT validation, strict row shape and timestamp
validation, preflight summary accounting, conflict detection against all stored
measurements, rollback/retry handling, credential-safe connection failures,
cross-platform project commands and isolated TimescaleDB CI.

Validation on 16 November: 43 tests passed plus 13 subtests against a disposable
TimescaleDB database. Full cleaning reproduced 903,522 accepted snapshots; all
loaded successfully. Full repeat import skipped exactly 903,522 identical rows.
Every stored field matches the canonical CSV. Evidence and samples are in
docs/evidence/. No source archive or existing contributor commits were changed.

Dependency: merge #27 first, then this PR. This branch includes its existing
commits without rewriting authorship. Related: #8. Reviewers perform merges.
Later PRs add queries/Grafana and submission materials.

Limitations: batches commit independently; partial imports can be resumed.
Source timezone and CPU semantics remain unconfirmed. Conflicting values are
reported and never silently treated as identical repeats.
