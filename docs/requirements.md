# Requirements and evidence map

Reviewed 16 November 2026: README, all repository documentation, every open and
closed issue/PR returned by GitHub (24 entries), issue comments, PR #27's two
commits and complete diff, and recent CI conclusions. Main is 98a2709; loader
PR head is 6be1b97. PR #27's initial CI failed, then its latest two runs passed.
Repository files contain no organiser poster template, grading rubric, original
project brief or presentation duration. Separate GitHub Discussions were not
available through the connected tooling; no discussion content is claimed as
reviewed. User-supplied deadline and mandatory deliverables are the submission
constraints until the organiser provides more detail.

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
| Journal (user/organiser request) | submission/journal.md | History-derived entries explicitly retrospective |
| VirtualBox cluster (#12 wording) | Linux-container deployment demonstrated | No evidence of a VirtualBox cluster; no claim that one was built |

## Decisions for a defensible submission

Preserve the existing pipeline and contributor history. Correct and extend the
loader rather than replace it. Use TimescaleDB and Grafana as requested by the
issue set. Preserve wall-clock timestamps; show them on a UTC-labelled plotting
axis only as a display convention, with an explicit on-screen caveat. Do not
invent missing metrics. Ask the organiser whether the VirtualBox wording is
applicable and whether the unavailable metrics need a separate dataset.

Keep issues open until teammates review the evidence and merge. A passing test
does not establish acceptance of a substituted metric or a submission format.
