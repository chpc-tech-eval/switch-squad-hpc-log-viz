# Switch Squad presentation

Editable narrative source. Speaker allocation and organiser timing remain to be confirmed.

## 1. From cluster logs to evidence

- Switch Squad · SCC 2026
- A reproducible historical HPC dashboard
- Prepared 16 November 2026

Speaker notes: Introduce the team. We process historical whole-cluster snapshots, not individual job histories.

## 2. Start with what the data supports

- 3,169 files; 917,919 nonblank source rows
- January 2017 to October 2025; roughly five-minute observations
- Reported CPU, node counts and aggregate job-state counts
- No node IDs, memory, job arrivals or completions

Speaker notes: Explain the photo-album analogy. A queued count is not a waiting-time measurement.

## 3. One traceable pipeline

- Validate both log formats; preserve NULLs
- Deduplicate identical rows; quarantine every conflicting timestamp
- Store accepted rows; analyse with SQL; explore in Grafana

Speaker notes: Point to each stage. Quality reports retain source locations and reasons. Linux containers carry the same workflow across hosts.

## 4. Quality is part of the result

- 903,522 accepted snapshots
- 12,489 extra identical duplicates
- 937 conflicting timestamps → 1,907 quarantined variants
- 1 rejected row; row accounting passes
- 9,084 missing CPU values; 212 reported CPU values above 100%

Speaker notes: These are actual full-archive counts. Warnings are events, not necessarily distinct bad rows. Missing values remain distinct from zero.

## 5. Explore the working dashboard

- Absolute date range + hour/day/week buckets
- CPU, job backlog, nodes and observation coverage
- Actual Grafana screenshot · 16 November 2026

Speaker notes: Show the interface. Its database role can SELECT but cannot modify snapshots. Point out the source-timezone caveat.

## 6. Observed findings, with context

- 70.97% mean reported CPU, across 894,438 CPU-present snapshots
- 98.63% highest daily mean with ≥200 CPU samples: 26 June 2025
- 2,536 maximum observed queued-job count
- Largest accepted-snapshot gap: 4 days, 5 minutes
- Snapshot-weighted results; changing capacity limits comparisons

Speaker notes: The peak day has 288 CPU samples. We do not infer causes. Exactly zero reported CPU does not prove the hardware was idle.

## 7. Trust comes from comparison

- All 903,522 rows and all 12 database fields match the clean CSV
- Repeat import: 0 inserted; 903,522 identical rows skipped
- 43 tests + 13 subtests pass with real TimescaleDB
- 36 panel-query checks; Chrome UI and bucket-click checks
- Linux tooling container independently verifies the stored data

Speaker notes: Explain the repaired loader: matching timestamps alone are not enough. A differing reimport is a reported failure. Batches commit independently and can be resumed.

## 8. An honest boundary

- CPU percentage semantics and source timezone remain unconfirmed
- No per-node usage, memory, throughput or individual wait time
- Missing buckets stay empty; no artificial snapshot records
- Local Linux-container deployment verified; no VirtualBox cluster claimed

Speaker notes: The issue text asks for metrics that this dataset cannot supply. We document substitutions and need organiser confirmation, rather than invent results.

## 9. Live demo: ask a narrower question

- Open the historical dashboard and its coverage panels
- Choose 26 June 2025; switch Bucket to 1 hour
- Hover CPU and queue-count series
- Show the verification evidence and CI
- Fallback: actual screenshots and PDF, clearly labelled

Speaker notes: Follow submission/demo.md. Allow six minutes if the organiser permits. Do not run the full import during the live demo.

## 10. What we accomplished

- Raw logs → validated storage → supported analysis → interactive dashboard
- Reproducible Linux/Windows workflow and real-database tests
- Evidence-backed poster, journal, slides and demo guide
- Next: confirm requirements and rehearse the presentation
- Repository: github.com/chpc-tech-eval/switch-squad-hpc-log-viz

Speaker notes: Conclude with the deliverables and remaining questions: source timezone, CPU units, organiser formats and unsupported metrics.
