import streamlit as st
from utils.styles import inject_css

st.set_page_config(
    page_title="F1 Analytics",
    page_icon="assets/f1_icon.png" if False else None,
    layout="wide",
)
inject_css()

st.title("F1 Analytics Pipeline")

st.markdown(
    """
    An end-to-end data engineering project ingesting Formula 1 race data from multiple
    sources, transforming it through BigQuery and dbt, and serving insights through this dashboard.

    Select a view from the sidebar.
    """
)

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
col1.markdown("**Ingestion**<br>FastF1 · Jolpica API · dlt · GCS", unsafe_allow_html=True)
col2.markdown("**Warehouse**<br>BigQuery · dbt Core", unsafe_allow_html=True)
col3.markdown("**Orchestration**<br>Apache Airflow · Docker", unsafe_allow_html=True)
col4.markdown("**Dashboard**<br>Streamlit Community Cloud", unsafe_allow_html=True)

st.markdown("---")
st.caption("Season: 2024 · 24 Races · [Source code](https://github.com/BModz/f1-analytics-pipeline)")
