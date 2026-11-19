# Switch Squad project journal

Prepared 18 November 2026.

## Retrospective repository record

Retrospective chronology compiled from Git commit dates, author metadata and validation records. Meeting attendance and person-hours are not inferred.

| Recorded date | Commit | Author | Recorded change |
|---|---|---|---|
| 2026-10-15 | 3b10e6c | Edwin | Add Windows Python setup and dependencies |
| 2026-10-21 | b340ca9 | Edwin | Set up Python environment documentation and project structure |
| 2026-11-03 | 6861868 | Katleho | Add initial exploratory analysis of HPC logs |
| 2026-11-05 | 6020ae4 | Jury Tsoka | Add HPC snapshot cleaning pipeline |
| 2026-11-05 | 86bac7f | Jury Tsoka | Fix HPC log cleaning and add regression tests |
| 2026-11-09 | 9d3ad67 | Tsholofelo Puseletso Mokapu | Extend cleaning tests and add GitHub Actions |
| 2026-11-09 | d637581 | Edwin | Set up local TimescaleDB for cluster snapshots |
| 2026-11-09 | 799ca31 | Jury Tsoka | Add batched HPC snapshot database loader |
| 2026-11-16 | 2591e86 | Edwin | Harden snapshot ingestion and verify real TimescaleDB transactions |
| 2026-11-16 | 5f7fbc7 | Edwin | Add historical SQL analysis and provisioned Grafana dashboard |
| 2026-11-16 | 3830f6f | Edwin | Prepare evidence-backed poster journal presentation and demo materials |
| 2026-11-16 | 5bf6d4f | Edwin | Refresh public documentation and presentation exports |

## Database loader development — retrospective

PR #27 by Jury Tsoka supplied a batched psycopg2 loader and mocked unit tests. Subsequent changes added required-field and BIGINT validation, conflict detection, real PostgreSQL integration tests, rollback recovery and full-dataset verification. The original contributor commits are preserved in repository history.

## 16 November 2026 — implementation and validation

Retrospective summary of repository changes and recorded validation results. Test evidence is stored in docs/evidence/.

1. Compared the supplied log fields with the project requirements and documented which metrics the aggregate snapshots can support.
2. Verified Python 3.13 and Linux containers through Docker Desktop on Windows. Added a Linux tooling container and reproducible setup instructions.
3. Reproduced cleaning: 3,169 files, 917,919 nonblank rows, 903,522 accepted, 12,489 extra identical duplicates, 937 conflicting timestamps (1,907 variants) and one rejected row.
4. Extended the loader with strict validation, conflict detection and preflight accounting. Real TimescaleDB tests verified repeat imports and rollback recovery. All 43 tests and 13 subtests passed on Windows and inside the Linux tooling container.
5. Loaded 903,522 accepted rows with zero failures. Reimport inserted zero and skipped 903,522 identical rows. Every row and all 12 fields matched the cleaned CSV; the Linux runner independently completed that comparison.
6. Implemented SQL analysis and provisioned Grafana. All 36 panel/bucket API checks passed; the full count was 903,522 and an empty range returned zero. Chrome rendered the dashboard and passed a real bucket-dropdown click. Actual screenshots were saved.
7. Prepared poster, slide, journal, demo and checklist sources/exports from the saved evidence. The implementation and materials were merged through PRs #27–30. Presentation rehearsal and final submission remain outstanding.

## Decisions, challenges and lessons

- The existing cleaner and schema provided the foundation for the ingestion and dashboard work.
- Identical timestamps require measurement comparison before a reimport can be classified as a duplicate.
- Real transactions expose rollback and constraint behaviour that mocked insert counts cannot establish.
- Aggregate snapshots support occupancy and backlog trends, but not individual waiting times or throughput.
- Unknown timezone, changing capacity, missing data and anomalous percentages limit interpretation.
- Linux containers provide a portable application deployment across Windows and Linux hosts.

## Evidence and outstanding requirements

Validation records are in docs/evidence/ and findings are in docs/analysis.md. On 17 November 2026, the mentor accepted the alternative metrics in issue #9 and the Linux-container deployment in issue #12. A separate VirtualBox cluster is not required. The final format, poster size and submission cutoff require organiser confirmation. Fresh-checkout reproduction and presentation rehearsal are tracked in submission/checklist.md.
