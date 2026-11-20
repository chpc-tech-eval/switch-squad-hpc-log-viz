# Switch Squad project journal

Updated 20 November 2026.

## Team contributions

Edwin, Jurry, Tsholo and Katleho worked collaboratively on a shared PC. The contribution summary below records three shared work areas for each teammate. These are collaborative contributions, not claims of exclusive authorship; the account used to commit a change does not identify everyone who worked on it.

| Teammate | Contribution 1 | Contribution 2 | Contribution 3 |
|---|---|---|---|
| Edwin | Shared Python environment and project setup | Shared database integration and deployment work | Shared documentation and submission preparation |
| Jurry | Shared log parsing and cleaning | Shared duplicate/conflict handling and quality reporting | Shared batched loading and repeat-import handling |
| Tsholo | Shared regression tests and CI | Shared validation and real-database checks | Shared deployment checks and demonstration preparation |
| Katleho | Shared exploratory data analysis | Shared historical SQL analysis and Grafana visualisation | Shared findings, limitations and presentation preparation |

## Retrospective repository record

Chronology compiled from Git commit dates and validation records. Commit identifiers link the shared work to repository history. Meeting attendance and person-hours are not inferred.

| Recorded date | Commit | Recorded change |
|---|---|---|
| 2026-10-15 | 3b10e6c | Add Windows Python setup and dependencies |
| 2026-10-21 | b340ca9 | Set up Python environment documentation and project structure |
| 2026-11-03 | 6861868 | Add initial exploratory analysis of HPC logs |
| 2026-11-05 | 6020ae4 | Add HPC snapshot cleaning pipeline |
| 2026-11-05 | 86bac7f | Fix HPC log cleaning and add regression tests |
| 2026-11-09 | 9d3ad67 | Extend cleaning tests and add GitHub Actions |
| 2026-11-09 | d637581 | Set up local TimescaleDB for cluster snapshots |
| 2026-11-09 | 799ca31 | Add batched HPC snapshot database loader |
| 2026-11-16 | 2591e86 | Harden snapshot ingestion and verify real TimescaleDB transactions |
| 2026-11-16 | 5f7fbc7 | Add historical SQL analysis and provisioned Grafana dashboard |
| 2026-11-16 | 3830f6f | Prepare evidence-backed poster journal presentation and demo materials |
| 2026-11-16 | 5bf6d4f | Refresh public documentation and presentation exports |
| 2026-11-19 | 0a20047 | Document accepted deployment and refresh submission materials |
| 2026-11-20 | cc6ac02 | Add files via upload |
| 2026-11-20 | 8d1d6f3 | Refresh project journal and validation exports |
| 2026-11-20 | 1b0b301 | Delete submission/checklist.md |

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

## 20 November 2026 — presentation and final review allocation

Responsibilities below cover presentation delivery and remaining review tasks. They do not replace the recorded development contributions or establish completion of the reviews.

| Teammate | Presentation responsibility | Final review responsibility |
|---|---|---|
| Edwin | Slides 1–2: introduction, project purpose and source data; opening demo context | Check submission files and repository links; confirm organiser submission channel and cutoff |
| Jurry | Slides 3 and 5: cleaning pipeline, quality accounting and ingestion; explain repeat imports | Review cleaning and loader explanations against saved quality and ingestion evidence |
| Tsholo | Slides 4 and 8: deployment, service connections and testing; show verification during the demo | Run presentation-laptop preflight checks and review saved validation evidence |
| Katleho | Slides 6–7: dashboard and findings; close on slide 11 | Review chart labels, reported findings and PDF readability against the analysis |

Shared slide 9: Edwin explains unavailable metrics; Jurry explains conflicting and missing values; Tsholo explains deployment acceptance; Katleho explains interpretation limits.

Shared slide 10 demonstration: Edwin introduces the historical range; Jurry explains accepted counts and duplicate handling; Katleho changes the date range and bucket and explains the charts; Tsholo opens verification evidence and explains the field comparison.

All four teammates rehearse their sections, check handovers and answer questions about how their section connects to the full pipeline. Presentation and review duties are distributed across the team; completion is recorded only after the relevant action is performed.

## 20 November 2026 — dashboard preparation

Checked that the local Grafana and database services were healthy. A corrected full-history dashboard URL using numeric epoch-millisecond endpoints displayed 903,522 accepted snapshots and 70.97% mean reported CPU. An invalid end date in 1970 explained an empty selected range. The external ngrok browser check timed out; public access was not confirmed.

## Decisions, challenges and lessons

- The existing cleaner and schema provided the foundation for the ingestion and dashboard work.
- Identical timestamps require measurement comparison before a reimport can be classified as a duplicate.
- Real transactions expose rollback and constraint behaviour that mocked insert counts cannot establish.
- Aggregate snapshots support occupancy and backlog trends, but not individual waiting times or throughput.
- Unknown timezone, changing capacity, missing data and anomalous percentages limit interpretation.
- Linux containers provide a portable application deployment across Windows and Linux hosts.

## Evidence and outstanding requirements

Validation records are in docs/evidence/ and findings are in docs/analysis.md. On 17 November 2026, the mentor accepted the alternative metrics in issue #9 and the Linux-container deployment in issue #12. A separate VirtualBox cluster is not required. The final format, poster size and submission cutoff require organiser confirmation. Fresh-checkout reproduction and presentation rehearsal are tracked in submission/checklist.md.
