# F1 Analytics Pipeline

An end-to-end data engineering portfolio project ingesting Formula 1 race data from multiple sources, transforming it in BigQuery, and serving insights through a live Streamlit dashboard.

> **Status:** 🚧 In progress — Week 1 of 6

---

## Architecture

```
FastF1 (race/lap/telemetry)  ─┐
OpenWeatherMap (race weather) ─┼──► dlt ──► GCS (data lake) ──► BigQuery ──► dbt ──► Streamlit
Ergast API (historical data)  ─┘

Orchestration: Apache Airflow (local Docker)
CI: GitHub Actions
```

> Architecture diagram image coming in Week 6.

---

## Stack

| Layer | Tool | Why |
|---|---|---|
| Ingestion | [dlt](https://dlthub.com/) | Schema inference, incremental loading, GCS + BQ destinations |
| Data lake | Google Cloud Storage | Raw files land here before warehouse loading |
| Warehouse | Google BigQuery | Serverless, SQL-native, generous free tier |
| Transformation | [dbt Core](https://docs.getdbt.com/) | Modular SQL, tests, lineage, docs |
| Orchestration | Apache Airflow (Docker) | Industry-standard scheduler, DAG-based dependencies |
| Dashboard | [Streamlit](https://streamlit.io/) | Fast Python dashboards, free Community Cloud hosting |
| CI | GitHub Actions | Tests on every PR |

---

## Project Structure

```
f1-analytics-pipeline/
├── .dlt/                  # dlt config (secrets gitignored)
├── .github/workflows/     # CI pipelines
├── airflow/dags/          # Airflow DAG definitions
├── dbt/f1_pipeline/       # dbt project (staging → intermediate → marts)
├── docs/                  # Architecture diagram + decisions log
├── exploration/           # Data exploration scripts
├── ingestion/             # dlt pipeline scripts (one per source)
├── tests/                 # pytest tests
├── docker-compose.yml     # Airflow local setup
└── pyproject.toml         # Python dependencies (managed with uv)
```

---

## Data Sources

| Source | Data | Frequency |
|---|---|---|
| [FastF1](https://docs.fastf1.dev/) | Race sessions, lap times, telemetry | Per race weekend |
| [OpenWeatherMap](https://openweathermap.org/api) | Race day weather at circuit location | Per race day |
| [Ergast API](http://ergast.com/mrd/) | Historical results, standings, driver/constructor data | Historical + current season |

---

## Honest Tradeoffs

- **Airflow runs locally** — in production this would run on a managed service (Cloud Composer, Astronomer, MWAA). Local Docker is used here to stay within the zero-cost constraint and to demonstrate orchestration concepts without cloud spend.
- **Free tier only** — this pipeline is designed to stay within GCP free tier limits (10 GB BigQuery storage, 1 TB queries/month). Not designed for production scale.

---

## Running Locally

> Setup instructions coming as the project is built out.

---

## Week-by-Week Build Log

- [x] Week 1: FastF1 → GCS → BigQuery → minimal dbt (end-to-end happy path)
- [ ] Week 2: Add OpenWeatherMap + Ergast sources
- [ ] Week 3: Airflow DAG orchestration
- [ ] Week 4: Advanced dbt (snapshots, incremental, custom tests, docs)
- [ ] Week 5: Streamlit dashboard
- [ ] Week 6: Full test suite, CI, polished README + architecture diagram

---

## Related Project

My first DE portfolio project: [Crypto Market Data Pipeline](https://github.com/BModz/crypto-data-pipeline) — CoinGecko → dlt → BigQuery → dbt → Streamlit.
