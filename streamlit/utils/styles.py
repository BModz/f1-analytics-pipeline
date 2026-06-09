import streamlit as st

F1_RED = "#E8002D"
DARK_CARD = "#1C1C1C"
BORDER = "#2A2A2A"

# 2024 constructor colours for charts
TEAM_COLOURS = {
    "Red Bull Racing": "#3671C6",
    "Ferrari": "#E8002D",
    "Mercedes": "#00D2BE",
    "McLaren": "#FF8000",
    "Aston Martin": "#358C75",
    "Alpine": "#0093CC",
    "Williams": "#00A3E0",
    "Haas F1 Team": "#B6BABD",
    "Kick Sauber": "#52E252",
    "RB": "#6692FF",
}

PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="#111111",
    plot_bgcolor="#111111",
    font=dict(color="#FFFFFF", family="sans-serif"),
    xaxis=dict(gridcolor="#2A2A2A", linecolor="#2A2A2A"),
    yaxis=dict(gridcolor="#2A2A2A", linecolor="#2A2A2A"),
    legend=dict(
        bgcolor="#1C1C1C",
        bordercolor="#2A2A2A",
        borderwidth=1,
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
    ),
    margin=dict(l=20, r=20, t=60, b=20),
)


def inject_css():
    st.markdown(
        """
        <style>
        /* Tighten top padding */
        .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }

        /* Page title underline */
        h1 {
            border-bottom: 2px solid #E8002D;
            padding-bottom: 0.4rem;
            margin-bottom: 1.2rem;
        }

        /* Metric cards */
        [data-testid="metric-container"] {
            background-color: #1C1C1C;
            border: 1px solid #2A2A2A;
            border-left: 3px solid #E8002D;
            border-radius: 4px;
            padding: 1rem 1.2rem;
        }
        [data-testid="stMetricLabel"] { color: #999999 !important; font-size: 0.8rem; }
        [data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 1.6rem; font-weight: 700; }

        /* Divider */
        hr { border-color: #2A2A2A; }

        /* Dataframe */
        .stDataFrame { border: 1px solid #2A2A2A; border-radius: 4px; }

        /* Selectbox / slider labels */
        label { color: #AAAAAA !important; font-size: 0.85rem; }

        /* Sidebar */
        [data-testid="stSidebar"] { background-color: #0D0D0D; border-right: 1px solid #2A2A2A; }
        </style>
        """,
        unsafe_allow_html=True,
    )
