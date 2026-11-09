BEGIN;

CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS public.cluster_snapshots (
    "timestamp" TIMESTAMP WITHOUT TIME ZONE PRIMARY KEY,
    jobs_running BIGINT NOT NULL CHECK (jobs_running >= 0),
    jobs_queued BIGINT NOT NULL CHECK (jobs_queued >= 0),
    jobs_held BIGINT CHECK (jobs_held >= 0),
    jobs_exiting BIGINT CHECK (jobs_exiting >= 0),
    nodes_running BIGINT NOT NULL CHECK (nodes_running >= 0),
    nodes_offline BIGINT NOT NULL CHECK (nodes_offline >= 0),
    nodes_total BIGINT NOT NULL CHECK (nodes_total >= 0),
    nodes_running_percent DOUBLE PRECISION CHECK (
        nodes_running_percent >= 0
        AND nodes_running_percent < 'Infinity'::DOUBLE PRECISION
    ),
    cpu_used BIGINT CHECK (cpu_used >= 0),
    cpu_total BIGINT CHECK (cpu_total >= 0),
    cpu_percent DOUBLE PRECISION CHECK (
        cpu_percent >= 0
        AND cpu_percent < 'Infinity'::DOUBLE PRECISION
    )
);

SELECT create_hypertable(
    'public.cluster_snapshots',
    by_range('timestamp', INTERVAL '30 days'),
    if_not_exists => TRUE
);

-- Preserve recorded times while the source timezone is unconfirmed.
-- Retain all historical records without automatic deletion.

COMMIT;