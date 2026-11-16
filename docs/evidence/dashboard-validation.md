# Dashboard and Linux validation — 16 November 2026

Verified locally with Grafana 12.3.0, running as a Linux container, and Chrome
157.0.8103.52 on Windows. Actual screenshots are in submission/assets/.

- Provisioned dashboard and datasource loaded successfully; Grafana reports healthy.
- All 12 SQL panels executed through Grafana for hour/day/week aggregation:
  36 successful panel query checks.
- Full-range count is exactly 903,522; a 2030 empty range returns zero.
- Chrome rendered the historical overview and a known filtered historical day.
- The Bucket dropdown was clicked and changed from daily to hourly aggregation.
- All observed datasource HTTP responses were 200; no browser page errors.
- Chart queries produce explicit NULL buckets for unobserved intervals; values
  are not interpolated. Statistics show exact counts and two CPU decimals.
- Linux Python tooling container compared every database row/field with the CSV.
- Linux disposable-database tests: 43 passed plus 13 subtests.

Machine-readable evidence: dashboard-api.json, browser-qa.json and
database-verification.json. SQL output and descriptive findings are preserved in
analysis.json and docs/analysis.md. Screenshot and API checks exercise rendering,
selected interactions and queries; they do not establish organiser acceptance or
every possible browser/device interaction. Manual drag-to-zoom rehearsal remains
part of the team's live-demo preparation.
