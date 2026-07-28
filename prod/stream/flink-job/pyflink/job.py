"""PyFlink entrypoint that submits the failure-statistics SQL job (ASC-030/031).

Reads ``sql/failure_stats.sql``, substitutes ``${KAFKA_BOOTSTRAP}`` from the environment, and
executes each statement on a streaming TableEnvironment. Packaged into the job image and submitted
to the Flink cluster by ``deploy/k3s/components/flink``.

Run locally against a Flink session cluster:
    KAFKA_BOOTSTRAP=kafka:9092 python pyflink/job.py
"""

from __future__ import annotations

import os
from pathlib import Path

SQL_FILE = Path(__file__).resolve().parent.parent / "sql" / "failure_stats.sql"


def load_statements(bootstrap: str) -> list[str]:
    raw = SQL_FILE.read_text().replace("${KAFKA_BOOTSTRAP}", bootstrap)
    # Strip full-line comments first (a comment may contain ';'), then split on statement ends.
    lines = [ln for ln in raw.splitlines() if not ln.strip().startswith("--")]
    cleaned = "\n".join(lines)
    return [stmt.strip() for stmt in cleaned.split(";") if stmt.strip()]


def main() -> None:  # pragma: no cover - requires a Flink runtime
    from pyflink.table import EnvironmentSettings, TableEnvironment

    bootstrap = os.environ.get("KAFKA_BOOTSTRAP", "kafka.data.svc.cluster.local:9092")
    t_env = TableEnvironment.create(EnvironmentSettings.in_streaming_mode())
    result = None
    for stmt in load_statements(bootstrap):
        result = t_env.execute_sql(stmt)
    # The final statement is the streaming INSERT; block on it so the (embedded or session)
    # Flink job keeps running and consuming instead of the driver exiting immediately.
    if result is not None:
        result.wait()


if __name__ == "__main__":
    main()
