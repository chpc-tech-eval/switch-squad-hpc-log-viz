# Switch Squad project journal

Prepared 16 November 2026.

## Retrospective repository record

The entries below are reconstructed from Git history, not contemporaneous diary entries. Dates, author display names and subjects are recorded as committed. Commit subjects establish recorded changes; they do not prove meeting attendance, hours worked, individual learning or task ownership beyond the authored commit. Main at inspection: 98a2709.

| Recorded date | Commit | Author | Recorded change |
|---|---|---|---|
| 2026-09-22 | 9e67f7d | Vuyolwethu Mfidi | Add files via upload |
| 2026-10-15 | 3b10e6c | Edwin | Add Windows Python setup and dependencies |
| 2026-10-15 | e8b3160 | Edwin | Fix README formatting and setup commands |
| 2026-10-21 | b340ca9 | Edwin | Set up Python environment documentation and project structure |
| 2026-10-21 | 4c559f8 | Edwin | Update setup.md |
| 2026-10-21 | 98f790e | Edwin | Document initial PBS snapshot structure |
| 2026-11-03 | 1cec8cf | Tsholofelo Puseletso Mokapu | Add dataset inventory documentation |
| 2026-11-03 | f515d3e | Tsholofelo Puseletso Mokapu | Add dataset inventory content |
| 2026-11-03 | 6861868 | Katleho | Add initial exploratory analysis of HPC logs |
| 2026-11-05 | 6020ae4 | Jury Tsoka | Add HPC snapshot cleaning pipeline |
| 2026-11-05 | 86bac7f | Jury Tsoka | Fix HPC log cleaning and add regression tests |
| 2026-11-09 | d06054b | Edwin | Document canonical cluster snapshot schema |
| 2026-11-09 | 9d3ad67 | Tsholofelo Puseletso Mokapu | Extend cleaning tests and add GitHub Actions |
| 2026-11-09 | d637581 | Edwin | Set up local TimescaleDB for cluster snapshots |

## Loader work awaiting review — retrospective

PR #27 by Jury Tsoka supplied a batched psycopg2 loader and mocked unit tests. Its inspected head was 6be1b979d1fc7bb39990b8a8648be71251c2255a. Its description explicitly left real PostgreSQL integration, rollback and full-data ingestion outstanding. Those commits were retained as the base of the completion branches.

## 16 November 2026 — completion-session record

Recorded from work actually performed in this session, with AI assistance under the repository owner's instruction. Commits use the checkout's existing Git identity; this entry does not assign the session's work to other teammates.

1. Reviewed documentation, all open/closed issues and PR listings, issue comments, the loader diff and recent CI. Reported an assessment and effort ranges before implementation.
2. Verified Windows/Python access, started Docker Desktop and confirmed Linux containers. The connected GitHub app was read-only; Git credentials allowed authorised feature pushes.
3. Reproduced cleaning: 3,169 files, 917,919 nonblank rows, 903,522 accepted, 12,489 extra identical duplicates, 937 conflicting timestamps (1,907 variants) and one rejected row.
4. Extended the loader with strict validation, conflict detection and preflight accounting. Real TimescaleDB tests verified repeat imports and rollback recovery. All 43 tests and 13 subtests passed on Windows and inside the Linux tooling container.
5. Loaded 903,522 accepted rows with zero failures. Reimport inserted zero and skipped 903,522 identical rows. Every row and all 12 fields matched the cleaned CSV; the Linux runner independently completed that comparison.
6. Implemented SQL analysis and provisioned Grafana. All 36 panel/bucket API checks passed; the full count was 903,522 and an empty range returned zero. Chrome rendered the dashboard and passed a real bucket-dropdown click. Actual screenshots were saved.
7. Prepared poster, slide, journal, demo and checklist sources/exports from the saved evidence. Review and rehearsal remain team tasks; no submission or merge is claimed.

## Decisions, challenges and lessons

- Keep useful existing work and accurate contributor history; make changes reviewable in dependent PRs.
- A matching timestamp does not prove matching measurements. Compare values before calling a repeat harmless.
- Real transactions reveal risks that mocked insert counts cannot establish.
- A cluster snapshot cannot reveal individual job waiting time or throughput. State what the dataset supports.
- Unknown timezone, changing capacity, missing data and anomalous percentages must remain visible.
- Linux containers make the Windows-hosted workflow portable without claiming a VirtualBox deployment.

## Evidence and work still requiring people

See docs/evidence/, docs/analysis.md and the linked review PRs. The organiser's rubric, poster size, cutoff time and original brief were not supplied. Team confirmation, review/merge, fresh-checkout reproduction and presentation rehearsal remain unchecked in submission/checklist.md. No invented meeting notes or hours are included.
