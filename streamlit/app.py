import streamlit as st

st.set_page_config(
    page_title="F1 Analytics",
    page_icon="🏎️",
    layout="wide",
)

st.title("🏎️ F1 Analytics Pipeline")
st.markdown(
    """
    A portfolio data engineering project — **FastF1 + Jolpica → GCS → BigQuery → dbt → Streamlit**.

    Use the sidebar to navigate between views.

    ---

    | Layer | Technology |
    |-------|-----------|
    | Ingestion | FastF1, Jolpica API, dlt, GCS |
    | Warehouse | BigQuery |
    | Transformation | dbt Core (staging → intermediate → marts) |
    | Orchestration | Apache Airflow (Docker) |
    | Dashboard | Streamlit Community Cloud |

    **Season:** 2024 · **Races:** 24 · **Source:** [GitHub](https://github.com/BModz/f1-analytics-pipeline)
    """
)
