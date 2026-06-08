"""
GCS → BigQuery load script.

Loads raw Parquet files from GCS into native BigQuery tables.
This is the "load" step of the ELT pattern — data moves from the
raw data lake (GCS) into the warehouse (BigQuery) for transformation.

Usage:
    python ingestion/gcs_to_bigquery.py --season 2024
"""

import argparse

from google.cloud import bigquery, storage
from google.oauth2 import service_account

GCP_PROJECT = "f1-analytics-pipeline"
GCS_BUCKET = "f1-analytics-pipeline-raw"
BQ_DATASET = "raw"
KEY_PATH = r"D:\secrets\f1-pipeline-key.json"

FASTF1_TABLES = {
    "race_results": "race_results",
    "race_laps": "race_laps",
    "race_weather": "race_weather",
}

JOLPICA_TABLES = {
    "drivers": "drivers",
    "constructors": "constructors",
    "driver_standings": "driver_standings",
    "constructor_standings": "constructor_standings",
}


def get_clients():
    creds = service_account.Credentials.from_service_account_file(KEY_PATH)
    bq = bigquery.Client(project=GCP_PROJECT, credentials=creds)
    gcs = storage.Client(project=GCP_PROJECT, credentials=creds)
    return bq, gcs


def ensure_dataset(bq: bigquery.Client):
    """Create the raw dataset in BigQuery if it doesn't exist."""
    dataset_ref = bigquery.Dataset(f"{GCP_PROJECT}.{BQ_DATASET}")
    dataset_ref.location = "US"
    bq.create_dataset(dataset_ref, exists_ok=True)
    print(f"Dataset `{BQ_DATASET}` ready.")


def list_parquet_files(gcs: storage.Client, prefix: str) -> list[str]:
    """Return gs:// URIs for all Parquet files under a GCS prefix."""
    bucket = gcs.bucket(GCS_BUCKET)
    blobs = bucket.list_blobs(prefix=prefix)
    uris = [
        f"gs://{GCS_BUCKET}/{blob.name}"
        for blob in blobs
        if blob.name.endswith(".parquet")
    ]
    return uris


def load_table(bq: bigquery.Client, table_name: str, uris: list[str]):
    """Load a list of GCS Parquet URIs into a BigQuery table."""
    table_ref = f"{GCP_PROJECT}.{BQ_DATASET}.{table_name}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        autodetect=True,
    )

    print(f"  Loading {len(uris)} file(s) → {table_ref} ...")
    load_job = bq.load_table_from_uri(uris, table_ref, job_config=job_config)
    load_job.result()  # Wait for the job to complete

    table = bq.get_table(table_ref)
    print(f"  Done. {table.num_rows:,} rows in `{table_ref}`.")


def run(season: int):
    bq, gcs = get_clients()
    ensure_dataset(bq)

    print(f"\nLoading {season} season data from GCS → BigQuery...\n")

    for gcs_folder, bq_table in FASTF1_TABLES.items():
        prefix = f"fastf1_{season}/{gcs_folder}/"
        uris = list_parquet_files(gcs, prefix)
        if not uris:
            print(f"  WARNING: No Parquet files found at gs://{GCS_BUCKET}/{prefix}")
            continue
        load_table(bq, bq_table, uris)

    for gcs_folder, bq_table in JOLPICA_TABLES.items():
        prefix = f"jolpica_{season}/{gcs_folder}/"
        uris = list_parquet_files(gcs, prefix)
        if not uris:
            print(f"  WARNING: No Parquet files found at gs://{GCS_BUCKET}/{prefix}")
            continue
        load_table(bq, bq_table, uris)

    print("\nAll tables loaded.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", type=int, default=2024)
    args = parser.parse_args()
    run(season=args.season)
