"""
F1 analytics pipeline DAG.

Orchestrates the full ELT pipeline:
  1. Ingest FastF1 data (race results, laps, weather) → GCS          [parallel]
  2. Ingest Jolpica data (drivers, constructors, standings) → GCS     [parallel]
  3. Load all GCS Parquet files → BigQuery raw dataset
  4. Run dbt staging models

Scheduled weekly on Mondays so new race data is picked up after each race weekend.
Can also be triggered manually with a `season` config param.
"""

import sys
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

DEFAULT_SEASON = 2024

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def _ingest_fastf1(**context):
    sys.path.insert(0, "/opt/airflow/ingestion")
    import fastf1_pipeline
    season = context["dag_run"].conf.get("season", DEFAULT_SEASON)
    fastf1_pipeline.run_pipeline(season=int(season))


def _ingest_jolpica(**context):
    sys.path.insert(0, "/opt/airflow/ingestion")
    import jolpica_pipeline
    season = context["dag_run"].conf.get("season", DEFAULT_SEASON)
    jolpica_pipeline.run_pipeline(season=int(season))


def _gcs_to_bigquery(**context):
    sys.path.insert(0, "/opt/airflow/ingestion")
    import gcs_to_bigquery
    season = context["dag_run"].conf.get("season", DEFAULT_SEASON)
    gcs_to_bigquery.run(season=int(season))


with DAG(
    dag_id="f1_pipeline",
    description="FastF1 + Jolpica → GCS → BigQuery → dbt",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule="0 6 * * MON",  # 06:00 UTC every Monday
    catchup=False,
    tags=["f1", "ingestion", "dbt"],
) as dag:

    ingest_fastf1 = PythonOperator(
        task_id="ingest_fastf1",
        python_callable=_ingest_fastf1,
    )

    ingest_jolpica = PythonOperator(
        task_id="ingest_jolpica",
        python_callable=_ingest_jolpica,
    )

    load_to_bigquery = PythonOperator(
        task_id="gcs_to_bigquery",
        python_callable=_gcs_to_bigquery,
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=(
            "cd /opt/airflow/dbt && "
            "dbt run --profiles-dir /opt/airflow/dbt --target prod"
        ),
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=(
            "cd /opt/airflow/dbt && "
            "dbt test --profiles-dir /opt/airflow/dbt --target prod"
        ),
    )

    dbt_snapshot = BashOperator(
        task_id="dbt_snapshot",
        bash_command=(
            "cd /opt/airflow/dbt && "
            "dbt snapshot --profiles-dir /opt/airflow/dbt --target prod"
        ),
    )

    # FastF1 and Jolpica ingest in parallel → BQ load → dbt run → test + snapshot in parallel
    [ingest_fastf1, ingest_jolpica] >> load_to_bigquery >> dbt_run >> [dbt_test, dbt_snapshot]
