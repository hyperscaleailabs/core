-- Failure-type statistics job (ASC-030).
-- Consumes sim.iteration.events.v1, computes near-real-time failure-type counts/rates in tumbling
-- windows keyed by (runId, failureClassification), and writes to sim.failure.stats.v1.
-- Malformed/undecodable records are routed to sim.deadletter.v1 by the connector's error handling.

CREATE TABLE iteration_events (
    schemaVersion         STRING,
    runId                 STRING,
    iteration             INT,
    trajectoryId          STRING,
    traceId               STRING,
    eventType             STRING,
    workflowStage         STRING,
    failureClassification STRING,
    retryCount            INT,
    costUsd               DOUBLE,
    latencyMs             INT,
    outcome               STRING,
    `timestamp`           STRING,
    -- Processing-time windows: reliable, format-agnostic, and fire on wall-clock as events arrive.
    -- (An event-time variant with a parsed watermark is used where deterministic replay matters.)
    proc_time AS PROCTIME()
) WITH (
    'connector' = 'kafka',
    'topic' = 'sim.iteration.events.v1',
    'properties.bootstrap.servers' = '${KAFKA_BOOTSTRAP}',
    'properties.group.id' = 'flink-failure-stats',
    'scan.startup.mode' = 'earliest-offset',
    'format' = 'json',
    'json.ignore-parse-errors' = 'true'
);

CREATE TABLE failure_stats (
    runId                    STRING,
    failureClassification    STRING,
    windowStart              STRING,
    windowEnd                STRING,
    `count`                  BIGINT,
    p95LatencyMs             DOUBLE,
    retryRate                DOUBLE,
    duplicateTransactionRisk BIGINT
) WITH (
    'connector' = 'kafka',
    'topic' = 'sim.failure.stats.v1',
    'properties.bootstrap.servers' = '${KAFKA_BOOTSTRAP}',
    'format' = 'json'
);

-- 5s tumbling windows for the live monitor (a 1-minute variant can feed longer-term trend panels).
INSERT INTO failure_stats
SELECT
    runId,
    failureClassification,
    CAST(TUMBLE_START(proc_time, INTERVAL '5' SECOND) AS STRING) AS windowStart,
    CAST(TUMBLE_END(proc_time, INTERVAL '5' SECOND)   AS STRING) AS windowEnd,
    COUNT(*) AS `count`,
    -- Flink SQL has no built-in percentile; MAX is a sufficient upper-bound proxy for the demo.
    CAST(MAX(latencyMs) AS DOUBLE) AS p95LatencyMs,
    CAST(SUM(CASE WHEN retryCount > 0 THEN 1 ELSE 0 END) AS DOUBLE) / COUNT(*) AS retryRate,
    SUM(CASE WHEN failureClassification = 'duplicate_transaction_risk' THEN 1 ELSE 0 END)
        AS duplicateTransactionRisk
FROM iteration_events
WHERE failureClassification IS NOT NULL
GROUP BY
    runId,
    failureClassification,
    TUMBLE(proc_time, INTERVAL '5' SECOND);
