# Initial PBS log review

## Source and format

The supplied dataset is stored in logs.zip.

The archive contains date-named .log files. Each sampled line
contains a timestamp followed by comma-separated key=value fields.
Each line represents a snapshot of the whole cluster.

The initial review examined the first 30 lines of
logs/2017-01-22.log.

## Fields observed

| Field | Meaning |
|---|---|
| timestamp | Date and time of the snapshot |
| jobs_running | Number of running jobs |
| jobs_queued | Number of queued jobs |
| nodes_running | Nodes reported as running |
| nodes_offline | Nodes reported as offline |
| nodes_total | Total reported node count |
| nodes_running_percent | Running nodes divided by total nodes, as a percentage |
| cpu_used | Reported CPU resources in use; precise definition requires confirmation |
| cpu_total | Total reported CPU capacity |
| cpu_percent | Used CPU resources divided by total CPU capacity, as a percentage |

## Sample observations

- The 30 sampled records cover 22 January 2017, 08:25 to 10:50.
- Consecutive timestamps in this sample are five minutes apart.
- The timezone is not stated.
- The first record reports 60 running jobs and 2 queued jobs.
- It reports 484 running nodes out of 1012, approximately 47.83%.
- It reports 3960 used CPU resources out of 24448,
  approximately 16.20%.
- Percentage values contain a trailing percent sign.
- Repeated metric values at different timestamps are valid
  observations and are not automatically duplicate records.

## Analysis supported by this sample

The observed fields support cluster-wide CPU resource trends,
node availability trends, and running and queued job counts.

The sample contains no individual job IDs, node IDs, memory
measurements, or per-job submission and start times.
Per-node usage and individual job waiting times cannot be
calculated from these fields alone.

The collection method for cpu_used needs confirmation before
treating it as measured processor activity rather than allocated
CPU resources.

## Further inspection

One archive filename uses spaces: 2017 07 24.log.
Other observed filenames use hyphens, such as 2017-01-22.log.

Full file counts, dataset coverage, timestamp gaps, and data quality
checks will be documented under Issue #2.