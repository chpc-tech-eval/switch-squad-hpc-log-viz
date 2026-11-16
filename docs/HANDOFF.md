# Review and presentation handoff

Prepared 16 November 2026. The full implementation and materials are on
`completion/submission`; `main` was deliberately left unchanged. No PR was merged
and no issue was closed. Local Grafana and TimescaleDB are healthy; the dashboard
is <http://127.0.0.1:3000/d/switch-squad-hpc>.

## Review and merge in this order

| Order | PR | Purpose | Current base |
|---|---|---|---|
| 1 | [#27](https://github.com/chpc-tech-eval/switch-squad-hpc-log-viz/pull/27) | Jurry's original loader work | main |
| 2 | [#28](https://github.com/chpc-tech-eval/switch-squad-hpc-log-viz/pull/28) | Ingestion fixes and database tests | issue-8-loader |
| 3 | [#29](https://github.com/chpc-tech-eval/switch-squad-hpc-log-viz/pull/29) | SQL, Grafana and Linux workflow | completion/ingestion |
| 4 | [#30](https://github.com/chpc-tech-eval/switch-squad-hpc-log-viz/pull/30) | Poster, journal, slides and demo | completion/dashboard |

The dependent bases keep each review focused. **Do not simply merge a child PR
into its current feature-branch base.** After the preceding PR reaches `main`,
open the next PR, click **Edit** beside its title, and change **base** to `main`
if GitHub has not already done so. Inspect the diff and wait for its CI before
merging. Prefer merge commits for this stack to preserve its existing ancestry.
If repository rules require squash/rebase, inspect the retargeted diff carefully
and resolve the stack before merging; no history rewrite has been performed here.
Keep #27 and #28 together in the review queue: #28 fixes correctness limitations
of the initial loader. All merging remains the team's responsibility.

## What was verified

- Full Windows and Linux cleaning: 3,169 files and 917,919 nonblank source rows;
  903,522 accepted snapshots. All row accounting passed.
- Initial load: 903,522 inserted, zero failures. Repeat import on Windows and
  Linux: zero inserted, 903,522 identical rows skipped, zero failures.
- Every database row and all 12 fields match the canonical CSV, including a
  separate Linux comparison. Archive and canonical tuple digests are recorded.
- Real TimescaleDB tests: 43 passed plus 13 subtests, on Windows and Linux.
- Grafana: 36 panel/bucket query checks, exact full count and empty range checks;
  Chrome rendering and bucket-dropdown interaction; actual saved screenshots.
- Exported PDFs: one A1 poster page, ten slide pages, three A4 journal pages.
  Editable PowerPoint structure and notes checked. Native PowerPoint rendering
  still needs the presentation laptop.
- PR #28 and #29 CI passed. Check the latest #30 CI at review time; CI is also
  configured to repeat full historical cleaning/import/comparison/Grafana checks.

Evidence is in [evidence/](evidence/), findings in [analysis.md](analysis.md), and
the current setup route in [workflow.md](workflow.md).

## Materials and remaining team actions

See [submission/README.md](../submission/README.md) for editable sources and PDF
exports, [demo.md](../submission/demo.md) for exact startup commands and the live
walkthrough, and [checklist.md](../submission/checklist.md) for sign-off.

The team must confirm organiser formats, poster size/template, presentation
duration, cutoff time/channel, roster and the VirtualBox wording. Confirm that
the documented substitutes for unavailable per-node/job metrics are acceptable.
Ask the provider about timezone and CPU counting semantics. Reproduce from a
fresh teammate checkout, inspect PowerPoint, assign speakers, rehearse, review
and merge, then submit. These are not claimed as completed.

The deadline supplied by the team is **Friday, 20 November 2026**. The code and
materials are ready for review; protect time now for those human checks.
