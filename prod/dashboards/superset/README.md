# Superset dashboards

Importable dashboard bundles, in Superset's native export format. These are the
**source of truth** for the analytics surface: the dashboards are not built by hand
in the Superset UI.

That distinction was learned rather than designed. Superset's metadata database in
the local stack is ephemeral, so a hand-built dashboard disappears on a pod restart
and cannot be recreated from a clone - which quietly makes every "the data is
visible in Superset" claim unreproducible. Committed bundles fix that.

| Bundle | Contents |
|--------|----------|
| `failure-analytics/` | *Agent Simulation - Failure Analytics*: failure types by events (pie), duplicate-transaction risk by run (bar), over the ClickHouse `failure_stats` dataset |

## Import

```bash
cd prod
bash deploy/scripts/import-superset-dashboards.sh
```

The script port-forwards the in-cluster Superset unless `--url` is given, imports
every bundle in this directory with `overwrite=true`, and then **reconciles each
chart's `query_context`**.

That last step is not optional. Superset's dashboard importer does not carry
`query_context` onto the chart record, and a chart without one renders in the
browser but returns `Chart has no query context saved` from
`/api/v1/chart/<id>/data`. The dashboard looks fine while being unverifiable from
CI - so the evidence collector treats an unqueryable chart as a failed hop, and the
importer repairs it.

## Export

To capture UI changes back into the repository:

```bash
# with a Superset access token
curl -H "Authorization: Bearer $TOKEN" \
  "$SUPERSET_URL/api/v1/dashboard/export/?q=%5B<dashboard-id>%5D" -o bundle.zip
unzip bundle.zip -d dashboards/superset/<bundle-name>
```

Database passwords are masked as `XXXXXXXXXX` on export and are re-supplied at
import time from `CH_PASSWORD`; never commit an unmasked `sqlalchemy_uri`.

## Grafana

Grafana dashboards live in [`../grafana/`](../grafana/) and are provisioned by the
Grafana chart's own file-based provisioning, so they need no import step.

## Specified but not yet built (x86 / Druid path)

The bundle above is what exists and is verified. The original analytics design
(ASC-033) specified five dashboards over the **Druid** datasources
`iteration_events` and `failure_stats`, populated by the Kafka indexing supervisors
in [`../../ingestion/druid/`](../../ingestion/druid/README.md). Druid ships no arm64
image, so on Apple Silicon the OLAP store is ClickHouse and only the two charts
above were built; the rest remain specification.

| Dataset | Shape |
|---------|-------|
| `iteration_events` | One row per emitted event; dimensions are the correlation IDs plus `failureClassification` and `outcome`; metrics are count, cost, latency (sum and max), retries |
| `failure_stats` | Flink windowed failure-type rows; metrics are count, p95 latency, duplicate-transaction risk |

| # | Dashboard | Shows |
|---|-----------|-------|
| 1 | Experiment Overview | Runs, success/recovered/failed split, decision distribution |
| 2 | Failure-Type Breakdown | Counts and rates by `failureClassification`, highlighting `duplicate_transaction_risk` |
| 3 | Cost vs Reliability | Mean cost against validation success, sized by iterations |
| 4 | Latency Distribution | p50/p95/p99 by run and failure type |
| 5 | Baseline vs Candidate | Side-by-side metric comparison |

Dashboards 1 and 4 correspond loosely to the two ClickHouse charts already built.
Completing the set on x86 is tracked as ASC-099 in
[../../docs/design/SDLC_SUMMARY.md](../../docs/design/SDLC_SUMMARY.md).
