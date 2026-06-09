# F1 Analytics Pipeline

[![CI](https://github.com/BModz/f1-analytics-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/BModz/f1-analytics-pipeline/actions/workflows/ci.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![dbt](https://img.shields.io/badge/dbt-1.9-orange.svg)](https://docs.getdbt.com/)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://f1-analytics-pipeline-pswm3dtbgbthwcobjbpkdq.streamlit.app)

An end-to-end data engineering portfolio project — ingesting Formula 1 race data from multiple sources, transforming it through a layered dbt project in BigQuery, orchestrating with Apache Airflow, and serving insights via a live Streamlit dashboard.

**[Live Dashboard →](https://f1-analytics-pipeline-pswm3dtbgbthwcobjbpkdq.streamlit.app)**

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Data Sources                                │
│  FastF1 (race/lap/weather)  Jolpica API (standings/drivers/teams)   │
└────────────────────────┬────────────────────────────────────────────┘
                         │ dlt (schema inference + Parquet)
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│              GCS Data Lake  (f1-analytics-pipeline-raw)             │
│         Raw Parquet files partitioned by source + season            │
└────────────────────────┬────────────────────────────────────────────┘
                         │ BigQuery Load Job (WRITE_TRUNCATE)
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    BigQuery Warehouse                                │
│  raw.*          → source tables (race_results, laps, standings …)   │
│  dbt_prod_staging.*      → typed + renamed views                    │
│  dbt_prod_intermediate.* → enriched views (joins, window functions) │
│  dbt_prod_marts.*        → business tables (incremental + full)     │
│  snapshots.*             → SCD Type 2 history                       │
└────────────────────────┬────────────────────────────────────────────┘
                         │ Streamlit + google-cloud-bigquery
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│           Streamlit Dashboard (Community Cloud)                     │
│  Season Overview · Race Results · Championship Battle               │
│  Constructor Battle · Driver Profile                                 │
└─────────────────────────────────────────────────────────────────────┘

Orchestration: Apache Airflow 2.9 (LocalExecutor, Docker Compose)
CI:            GitHub Actions — pytest + dbt compile on every push/PR
```

---

## Stack

| Layer | Tool | Why |
|---|---|---|
| Ingestion | [dlt](https://dlthub.com/) + FastF1 + Jolpica API | Schema inference, Parquet output, GCS destination |
| Data lake | Google Cloud Storage | Raw files before warehouse load — reprocessable, auditable |
| Warehouse | Google BigQuery | Serverless SQL, generous free tier |
| Transformation | [dbt Core](https://docs.getdbt.com/) 1.9 | Modular SQL, lineage, tests, snapshots, incremental models |
| Orchestration | Apache Airflow 2.9 (Docker) | DAG-based dependencies, retry logic, web UI |
| Dashboard | [Streamlit](https://streamlit.io/) | Fast Python dashboards, free Community Cloud hosting |
| CI | GitHub Actions | pytest + dbt compile on every PR |
| Package manager | [uv](https://github.com/astral-sh/uv) | Fast Python packaging |

---

## Project Structure

```
f1-analytics-pipeline/
├── .github/workflows/      # CI — pytest + dbt compile
├── airflow/
│   ├── dags/               # f1_pipeline DAG
│   ├── Dockerfile          # Custom Airflow image with our deps
│   └── requirements.txt
├── dbt/f1_pipeline/
│   ├── models/
│   │   ├── staging/        # Clean + type-cast raw sources (views)
│   │   ├── intermediate/   # Joins + window functions (views)
│   │   └── marts/          # Business tables (incremental + full refresh)
│   ├── snapshots/          # SCD Type 2 — driver standings history
│   └── tests/              # Singular data quality tests
├── docs/
│   └── decisions.md        # Architecture & design decisions log
├── ingestion/
│   ├── fastf1_pipeline.py  # FastF1 → GCS via dlt
│   ├── jolpica_pipeline.py # Jolpica API → GCS via dlt
│   └── gcs_to_bigquery.py  # GCS Parquet → BigQuery raw dataset
├── streamlit/
│   ├── app.py              # Home page
│   ├── pages/              # 5 dashboard pages
│   ├── utils/bigquery.py   # BQ client + cached queries
│   └── requirements.txt
├── tests/                  # pytest unit tests
├── docker-compose.yml      # Airflow local setup
└── pyproject.toml          # Python deps (uv)
```

---

## Data Sources

| Source | Data | Update Frequency |
|---|---|---|
| [FastF1](https://docs.fastf1.dev/) | Race results, lap times, trackside weather | Per race weekend |
| [Jolpica API](https://api.jolpi.ca/) | Driver/constructor standings, biographical data | Per race round |

---

## dbt Model Lineage

```
raw.race_results ──────────────────────────────────────────────────────┐
raw.drivers      ──► stg_race_results ──► int_race_results_enriched ──► mart_race_results (table)
raw.constructors ──► stg_drivers      ─┐
                                       ├──► int_championship_progression ──► mart_driver_standings (incremental)
raw.driver_standings ──► stg_driver_standings ─┘                        ──► snap_driver_standings (SCD2)

raw.constructor_standings ──► stg_constructor_standings ──► mart_constructor_standings (table)
```

21 schema tests + 1 singular test (`assert_points_non_negative`).

---

## Running Locally

### Prerequisites

- Python 3.11+, [uv](https://github.com/astral-sh/uv)
- Docker Desktop
- GCP service account with BigQuery + GCS permissions → save key to `D:\secrets\f1-pipeline-key.json`

### 1. Clone & install

```bash
git clone https://github.com/BModz/f1-analytics-pipeline.git
cd f1-analytics-pipeline
uv sync
```

### 2. Configure secrets

```bash
# dlt GCS destination
cp .dlt/secrets.toml.example .dlt/secrets.toml
# Edit .dlt/secrets.toml — add your GCS bucket credentials
```

### 3. Start Airflow

```bash
# Create .env.airflow with your key path
echo "GCP_KEY_PATH=D:\secrets\f1-pipeline-key.json" > .env.airflow

docker compose --env-file .env.airflow up airflow-init --build
docker compose --env-file .env.airflow up -d
```

Open `http://localhost:8080` (admin / admin), trigger the `f1_pipeline` DAG.

### 4. Run the dashboard

```bash
cd streamlit
uv run streamlit run app.py
```

### 5. Run tests

```bash
uv run pytest tests/ -v
```

---

## Honest Tradeoffs

- **Airflow runs locally** — in production this would run on a managed service (Cloud Composer, Astronomer, MWAA). Local Docker demonstrates the same concepts within a zero-cost constraint.
- **Full reload on ingestion** — `write_disposition='replace'` reloads all 24 rounds each run. A production pipeline would use incremental ingestion keyed on round number.
- **Free tier only** — designed to stay within GCP free tier limits (10 GB BigQuery storage, 1 TB queries/month).
- **Streamlit Community Cloud** — spins down inactive apps, limited compute. Adequate for a portfolio dashboard with occasional visitors.

---

## Design Decisions

Non-obvious decisions and their rationale are logged in [`docs/decisions.md`](docs/decisions.md).

---

## Related Project

[Crypto Market Data Pipeline](https://github.com/BModz/crypto-data-pipeline) — CoinGecko → dlt → BigQuery → dbt → Streamlit.

---

## Week-by-Week Build Log

- [x] Week 1: FastF1 → GCS → BigQuery → minimal dbt (end-to-end happy path)
- [x] Week 2: Jolpica API source, full staging layer (7 models)
- [x] Week 3: Airflow DAG orchestration in Docker
- [x] Week 4: Advanced dbt — intermediates, marts, incremental model, SCD2 snapshot, 21 tests
- [x] Week 5: Streamlit dashboard (5 views) deployed to Community Cloud
- [x] Week 6: pytest suite, GitHub Actions CI, README + decisions log polish
