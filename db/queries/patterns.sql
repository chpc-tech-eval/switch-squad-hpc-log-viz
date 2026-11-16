-- ISO weekday: Monday=1, Sunday=7. Source wall-clock hour; timezone unconfirmed.
SELECT extract(isodow FROM timestamp)::int AS iso_weekday,
       extract(hour FROM timestamp)::int AS hour,
       count(*) AS samples, count(cpu_percent) AS cpu_samples,
       avg(cpu_percent) AS mean_reported_cpu_percent,
       avg(jobs_queued) AS mean_queued_jobs
FROM public.cluster_snapshots GROUP BY 1, 2 ORDER BY 1, 2;
