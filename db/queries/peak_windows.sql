-- Hour/day/week peak windows, each with its observed sample count.
WITH windows AS (
    SELECT 'hour' AS resolution, time_bucket(INTERVAL '1 hour', timestamp) AS start,
           count(*) AS samples, count(cpu_percent) AS cpu_samples, avg(cpu_percent) AS mean_reported_cpu_percent
    FROM public.cluster_snapshots GROUP BY 2
    UNION ALL
    SELECT 'day', time_bucket(INTERVAL '1 day', timestamp), count(*), count(cpu_percent), avg(cpu_percent)
    FROM public.cluster_snapshots GROUP BY 2
    UNION ALL
    SELECT 'week', time_bucket(INTERVAL '1 week', timestamp), count(*), count(cpu_percent), avg(cpu_percent)
    FROM public.cluster_snapshots GROUP BY 2
), ranked AS (
    SELECT *, row_number() OVER (PARTITION BY resolution ORDER BY mean_reported_cpu_percent DESC NULLS LAST, start) AS rank
    FROM windows WHERE cpu_samples > 0
) SELECT * FROM ranked WHERE rank <= 5 ORDER BY resolution, rank;
