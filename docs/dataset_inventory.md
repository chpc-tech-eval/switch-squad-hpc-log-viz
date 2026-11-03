\# Dataset Inventory



\## Overview



The HPC log dataset is stored in \*\*logs.zip\*\* and contains \*\*3,169 log files\*\*. Each log file represents monitoring data for a single day and contains multiple timestamped records describing the state of the HPC cluster.



\## Dataset Structure



\- Dataset file: `logs.zip`

\- Number of log files: \*\*3,169\*\*

\- File format: `.log`

\- Record format: Plain text

\- Timestamp interval: Approximately every 5 minutes



\## Example File Names



\- `logs/2017 07 24.log`

\- `logs/2017-01-22.log`

\- `logs/2017-01-23.log`

\- `logs/2017-01-24.log`

\- `logs/2017-01-25.log`



\## Fields



| Field | Description |

|--------|-------------|

| Timestamp | Date and time the statistics were recorded |

| jobs\_running | Number of jobs currently running |

| jobs\_queued | Number of jobs waiting to run |

| nodes\_running | Number of compute nodes currently running |

| nodes\_offline | Number of offline nodes |

| nodes\_total | Total number of nodes in the cluster |

| nodes\_running\_percent | Percentage of nodes currently running |

| cpu\_used | Number of CPUs currently in use |

| cpu\_total | Total CPUs available |

| cpu\_percent | Percentage of CPU utilisation |



\## Example Record



```text

2017-01-22 08:25, jobs\_running=60, jobs\_queued=2, nodes\_running=484, nodes\_offline=17, nodes\_total=1012, nodes\_running\_percent=47.83%, cpu\_used=3960, cpu\_total=24448, cpu\_percent=16.20%

```



\## Summary



The dataset provides time-series monitoring information for an HPC cluster. Each record captures workload activity, node availability, and CPU utilisation, making the dataset suitable for trend analysis, utilisation dashboards, and operational monitoring.



