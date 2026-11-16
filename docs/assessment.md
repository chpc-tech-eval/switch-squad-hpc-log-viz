# Initial assessment and estimate — 16 November 2026

Reported to the team before implementation edits. Main was 98a2709 and loader
PR #27 was 6be1b97. The decision was to retain cleaning/schema work and preserve
Jurry's loader commits, then correct ingestion and add the missing workflow.

Complete in source: cleaning/quarantine, schema, database configuration, cleaning
CI. Partial/unverified: loader validation, real database integration and full
ingestion. Missing: query set, analysis, Grafana, complete Linux instructions,
poster, journal, slides and demo. Original cleaning totals required reproduction.

The recommended route was Linux containers on the existing Windows laptop,
using the same Compose files on a Linux host. Docker initially was not running;
starting Docker Desktop restored access. Python 3.13.14 worked outside the
sandbox. GitHub's connected app was read-only, but Git's separate credentials
allowed feature branch pushes and PR creation. No merge permission was used.

Planning estimate: 12–20 focused hours for ingestion/queries/dashboard/validation,
6–10 for reproducibility/CI/docs, 6–10 for submission materials, plus 4–8 team
review/rehearsal hours. Waiting for downloads, CI, credentials or organiser
answers was additional and uncertain. These are planning ranges, not logged
person-hours or claims about actual time spent.

A focused submission by Friday, 20 November appeared feasible if materials time
was protected. Priorities were reliable ingestion, supported metrics, a working
Grafana demo, evidence and mandatory materials. No template/rubric/original brief
was present in the inspected files or issue text. Exact format, VirtualBox wording
and acceptance of unavailable-metric substitutions needed external confirmation.

Subsequent completed checks are recorded separately in docs/evidence/.
