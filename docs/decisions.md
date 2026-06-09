# Architecture & Design Decisions

A log of non-obvious decisions made during the build. Useful for interviews and for future-me.

---

## 2026-06-08 — Separate GCP project for F1 pipeline

**Decision:** Created a new GCP project (`f1-analytics-pipeline`) instead of reusing `crypto-pipeline-dev`.

**Why:** Clean separation between portfolio projects. Each project gets its own free tier quotas (10 GB BigQuery storage, 1 TB queries/month, GCS free egress). Better presentation when sharing GCP console screenshots with recruiters.

**Tradeoff:** ~10 minutes of extra setup. Worth it.

---

## 2026-06-08 — Data lake pattern: GCS before BigQuery

**Decision:** Raw data lands in GCS first, then gets loaded into BigQuery. Not loaded directly into BigQuery.

**Why:** This is the standard production data lake pattern. In real pipelines, raw files in object storage are:
- Cheaper to store than BigQuery rows
- Reprocessable — if a dbt model has a bug, you can reload from GCS without re-calling the API
- Auditable — you always have the original raw payload

**Tradeoff:** Extra step vs. loading directly to BQ. The extra step is the point — it's what separates a "data lake + warehouse" architecture from a simple pipeline.

---

## 2026-06-08 — Airflow runs locally in Docker, not on a managed service

**Decision:** Apache Airflow runs on localhost via Docker Compose, not on Cloud Composer, Astronomer, or MWAA.

**Why:** All managed Airflow services cost money. This is a portfolio project with a zero-budget constraint. Running Airflow locally in Docker is standard for development environments and demonstrates the same orchestration concepts.

**Tradeoff:** Not production-ready (no HA, no cloud scheduler). The README acknowledges this explicitly.

---

## 2026-06-09 — Jolpica instead of Ergast API

**Decision:** Used the Jolpica API (`api.jolpi.ca/ergast`) instead of the original Ergast API.

**Why:** Ergast shut down at the end of 2024. Jolpica is a community-maintained mirror with an identical response schema, so zero code changes were needed beyond the base URL.

**Tradeoff:** Jolpica is community-run with no SLA. Rate limits are stricter than Ergast was — required adding 1s sleeps between round requests and 429 retry logic with exponential back-off.

---

## 2026-06-09 — dbt three-layer architecture (staging → intermediate → marts)

**Decision:** Three distinct dbt layers rather than going straight from staging to marts.

**Why:** Intermediate models encapsulate joins and window functions so marts stay readable. Each layer has a single responsibility: staging cleans raw types, intermediate enriches and joins, marts are business-facing aggregations. This mirrors what you'd see in a production analytics engineering setup.

**Tradeoff:** More files and more indirection. For a project of this size, one layer would be sufficient — the three-layer approach is deliberate over-engineering to demonstrate the pattern.

---

## 2026-06-09 — Incremental model for mart_driver_standings

**Decision:** `mart_driver_standings` uses `materialized='incremental'` rather than a full table refresh.

**Why:** In a real weekly pipeline, only the latest race round is new. Reprocessing 24 rounds of standings every Monday is wasteful. The incremental model appends only rounds not already present in the target table.

**Tradeoff:** The raw standings table uses `write_disposition='replace'` (full reload), so all rounds are always in BigQuery regardless. The incremental benefit is in the dbt transformation step, not the ingestion step. In production you would pair this with incremental ingestion too.

---

## 2026-06-09 — SCD Type 2 snapshot on driver standings

**Decision:** `snap_driver_standings` uses dbt's `snapshot` with `strategy='check'` on position, points, and wins columns.

**Why:** Snapshots let you answer "who was leading the championship after round 12?" even after the season ends and the raw table is overwritten. This is the standard slowly-changing dimension pattern for audit and historical analysis.

**Tradeoff:** The `check` strategy re-scans all rows on every run. For large tables, `timestamp` strategy (based on an updated_at column) is more efficient — but the standings data has no updated_at column so `check` is the only option here.

---

## 2026-06-09 — Streamlit Community Cloud for dashboard hosting

**Decision:** Dashboard deployed to Streamlit Community Cloud rather than Cloud Run, App Engine, or a self-hosted VM.

**Why:** Streamlit Community Cloud is free for public repos, requires zero infrastructure setup, and deploys directly from GitHub. The dashboard is read-only (queries BigQuery) so there are no statefulness requirements.

**Tradeoff:** Streamlit Community Cloud has limited compute (1 vCPU, 1 GB RAM) and spins down inactive apps. Not suitable for production traffic. For a portfolio project with occasional visitors, it is perfectly adequate.

---
