import os

import pandas as pd
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

PROJECT = "f1-analytics-pipeline"
MARTS = "dbt_prod_marts"


@st.cache_resource
def get_client() -> bigquery.Client:
    try:
        secret = st.secrets["gcp_service_account"]
        creds = service_account.Credentials.from_service_account_info(secret)
    except Exception:
        key_path = os.environ.get(
            "GOOGLE_APPLICATION_CREDENTIALS",
            r"D:\secrets\f1-pipeline-key.json",
        )
        creds = service_account.Credentials.from_service_account_file(key_path)
    return bigquery.Client(project=PROJECT, credentials=creds)


@st.cache_data(ttl=3600)
def query(sql: str) -> pd.DataFrame:
    return get_client().query(sql).to_dataframe()


def table(name: str) -> str:
    return f"`{PROJECT}.{MARTS}.{name}`"
