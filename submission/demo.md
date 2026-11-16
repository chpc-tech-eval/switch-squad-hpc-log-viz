# Live demo and teammate walkthrough

## Explain it in plain language

The archive is a photo album of the cluster: each row describes the whole
cluster at one moment. The cleaner reads both log formats, checks values and
dates, and keeps an explanation for discarded or questionable rows. Identical
repeats count once. If two rows disagree about the same moment, neither enters
the clean dataset until the conflict is resolved. We never make up missing data.

The loader puts accepted rows into TimescaleDB. It checks that reruns really are
identical instead of just ignoring matching dates. SQL groups observations into
hours, days or weeks. Grafana asks those SQL questions and draws the results.
Its database account can read the snapshots but cannot change them.

903,522 is the accepted snapshot count, not the number of jobs. 70.97% is the
average *reported* CPU percentage of snapshots with a CPU value. It is not a
guarantee of hardware busy time, nor a time-weighted average over missing periods.

## Before presenting — Windows PowerShell

Open PowerShell in the repository root. Start Docker Desktop, then:

```powershell
docker --context desktop-linux compose up -d --wait db grafana
.\.venv\Scripts\python.exe -m scripts.check_dashboard
```

Stop if either command fails. Expected: healthy services, 36 panel query checks
pass, full-range snapshot count 903,522 and empty-range count zero. Open
<http://127.0.0.1:3000/d/switch-squad-hpc>. Keep the PDF slides and screenshots
available offline. Do not run a full clean/import during the presentation.

## Six-minute demo script (adjust after duration is confirmed)

1. **0:00–0:45 — Purpose.** Show the default historical range. Explain the
   cluster-snapshot model and point to the timezone caveat.
2. **0:45–1:30 — Trust.** Show the exact accepted count, missing CPU count and
   coverage panel. Explain quarantine and why missing is different from zero.
3. **1:30–2:30 — Explore.** Choose Bucket → 1 hour. Use the date picker to select
   26 June 2025 00:00 to 27 June 2025 00:00, using the displayed source-clock
   convention. Hover CPU and jobs. Queued counts are backlog, not waiting time.
   A ready link is
   <http://127.0.0.1:3000/d/switch-squad-hpc?from=1750896000000&to=1750982400000&var-bucket=1%20hour>.
4. **2:30–3:15 — Compare.** Return to the full historical range and daily buckets.
   Explain the peak-daily table's 200 CPU-sample rule and changing cluster size.
5. **3:15–4:15 — Evidence.** Show docs/evidence/database-verification.json:
   every stored field matches the CSV. Show the passing integration CI jobs.
6. **4:15–5:15 — Engineering.** Show the pipeline diagram. Explain identical
   reimports, explicit conflict failures, persistent storage and Linux containers.
7. **5:15–6:00 — Limits.** No job identifiers, arrivals/completions, per-node CPU,
   memory or confirmed timezone. We document those limits rather than invent them.

## Failure fallback

If Docker is unavailable, show `assets/dashboard-overview.png` and
`assets/dashboard-filtered.png`, clearly saying these are screenshots captured
from the working system on 16 November. Use `slides.pdf` and the saved evidence.
Do not describe this fallback as a live demo. Do not reinstall tools or reset
volumes during the presentation. If the date range is empty, restore the known
historical range; the dataset ends in October 2025, not today.

## Questions everyone should be able to answer

- **Why Linux?** The database and Grafana run as Linux containers; the same
  Compose files run on a Linux host. Windows is the editor/host in our verification.
- **Why TimescaleDB?** SQL fits the canonical table and time buckets support the
  historical queries. We retained the team's existing storage work.
- **Why no throughput?** Counting running jobs does not reveal how many finished.
- **Why values over 100?** They are reported source values; semantics need provider
  confirmation. We preserve and flag them so the evidence remains auditable.
- **What did we accomplish?** A reproducible raw-to-dashboard pipeline, tested
  ingestion, honest trend analysis, and reviewable code and submission materials.

Assign speakers and rehearse together; this document does not assert that a
rehearsal or any individual teammate's work has already happened.
