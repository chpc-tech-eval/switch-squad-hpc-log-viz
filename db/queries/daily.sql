SELECT time_bucket(INTERVAL '1 day', timestamp) AS day,
       count(*) AS samples, count(cpu_percent) AS cpu_samples,
       avg(cpu_percent) AS mean_reported_cpu_percent,
       max(cpu_percent) AS peak_reported_cpu_percent,
       avg(jobs_running) AS mean_running_jobs,
       avg(jobs_queued) AS mean_queued_jobs,
       max(jobs_queued) AS peak_queued_jobs,
       avg(nodes_running_percent) AS mean_reported_running_node_percent
FROM public.cluster_snapshots GROUP BY 1 ORDER BY 1;
