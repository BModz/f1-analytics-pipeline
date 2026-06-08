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

**Tradeoff:** Not production-ready (no HA, no cloud scheduler). The README will acknowledge this explicitly.

---
