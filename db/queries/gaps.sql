-- No synthetic rows: report discontinuities in accepted snapshots.
WITH intervals AS (
    SELECT lag(timestamp) OVER (ORDER BY timestamp) AS previous, timestamp AS next
    FROM public.cluster_snapshots
) SELECT previous, next, next - previous AS gap
FROM intervals WHERE next - previous > INTERVAL '5 minutes'
ORDER BY gap DESC, previous LIMIT 20;
