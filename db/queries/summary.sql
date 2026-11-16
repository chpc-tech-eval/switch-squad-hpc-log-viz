-- Means are snapshot-weighted; CPU percentage is reported, not confirmed hardware busy time.
SELECT count(*) AS snapshots, min(timestamp) AS first_timestamp,
       max(timestamp) AS last_timestamp,
       avg(cpu_percent) AS mean_reported_cpu_percent,
       min(cpu_percent) AS min_reported_cpu_percent,
       max(cpu_percent) AS max_reported_cpu_percent,
       count(cpu_percent) AS cpu_samples,
       count(*) FILTER (WHERE cpu_percent IS NULL) AS missing_cpu_samples,
       count(*) FILTER (WHERE cpu_percent > 100) AS cpu_above_100_samples,
       count(*) FILTER (WHERE cpu_percent = 0) AS zero_reported_cpu_samples,
       avg(jobs_running) AS mean_running_jobs, max(jobs_queued) AS max_queued_jobs,
       avg(jobs_queued) AS mean_queued_jobs,
       count(*) FILTER (WHERE nodes_running + nodes_offline > nodes_total) AS inconsistent_node_samples
FROM public.cluster_snapshots;
