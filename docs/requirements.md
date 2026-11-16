# Requirements and evidence map

This map relates the project issues to the implemented pipeline and its data
limitations. Implementation and submission materials were merged through
PRs #27–30. Issues #8, #10 and #11 are complete; #9 and #12 remain open for
clarification of unavailable metrics and deployment expectations.

Discussion #13 identifies the supplied raw archive. Discussion #16 recommends
Linux development and suggests Ubuntu through WSL2. Issue #12 mentions a
VirtualBox cluster deployment; whether that is required alongside this
application needs confirmation. Poster format, presentation duration and final
submission details also require organiser confirmation.

| Requirement | Evidence / implementation | Limitation |
|---|---|---|
| Inventory and cleaning (#2–4) | logs.zip; clean_logs.py; companion CSVs | Timezone unknown; conflicts quarantined |
| Canonical schema (#5) | docs/schema.md; db/schema.sql | Aggregate cluster fields only |
| Tests and CI (#6) | Cleaning, loader and disposable TimescaleDB tests | Browser QA is a separate local check |
| Historical storage (#7–8) | Pinned TimescaleDB; idempotent, validated loader | Batch commits; failed imports can be partial |
| CPU over time (#9) | Reported cluster CPU series | Per-node CPU impossible without node identifiers |
| Hour/day/week peaks (#9) | db/queries/peak_windows.sql | Snapshot means; coverage differs |
| Throughput and queue wait (#9) | Running/queued count trends instead | No job arrivals, completions or job histories; cannot calculate requested metrics |
| Patterns and report (#10) | patterns.sql; docs/analysis.md | Changing capacity and gaps limit interpretation |
| Grafana and interaction (#11) | Provisioned date filter, bucket selector, zoom, coverage panels | Historical dataset, not a live collection agent |
| Poster, slides, demo (#12) | submission/ | Final team review and format confirmation required |
| Project journal | submission/journal.md | History-derived entries explicitly retrospective |
| VirtualBox cluster (#12 wording) | Linux-container deployment demonstrated | No evidence of a VirtualBox cluster; no claim that one was built |

## Implementation decisions

The implementation extends the existing cleaner and database loader and
preserves contributor history. TimescaleDB stores the canonical snapshots;
Grafana provides the interactive view. Recorded wall-clock timestamps are
preserved. The UTC-labelled plotting axis is a display convention, with an
on-screen explanation. Unsupported metrics are documented rather than inferred
from unrelated aggregate counters.

Issues #9 and #12 remain open until the outstanding metric and deployment
questions are resolved. Validation results do not establish organiser approval
of a substituted metric or submission format.
