import streamlit as st

F1_RED = "#E8002D"
DARK_CARD = "#1C1C1C"
BORDER = "#2A2A2A"

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
    font=dict(color="#FFFFFF", family="Inter, sans-serif"),
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


def inject_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');

        /* Container */
        .block-container { padding-top: 1.2rem; padding-bottom: 1rem; }

        /* Global font */
        html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

        /* h1 fallback (st.title) */
        h1 { border-bottom: 2px solid #E8002D; padding-bottom: 0.4rem; margin-bottom: 1.2rem; }

        /* Metric cards */
        [data-testid="metric-container"] {
            background-color: #161616;
            border: 1px solid #252525;
            border-left: 3px solid #E8002D;
            border-radius: 4px;
            padding: 1rem 1.2rem;
        }
        [data-testid="stMetricLabel"] { color: #666 !important; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; }
        [data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 1.6rem; font-weight: 700; }
        [data-testid="stMetricDelta"] { font-size: 0.78rem; }

        /* Divider */
        hr { border-color: #1C1C1C; }

        /* Dataframe */
        .stDataFrame { border: 1px solid #222; border-radius: 4px; }

        /* Selectbox / slider labels */
        label { color: #888 !important; font-size: 0.8rem; }

        /* Sidebar */
        [data-testid="stSidebar"] { background-color: #0A0A0A; border-right: 1px solid #1C1C1C; }

        /* Selectbox */
        [data-testid="stSelectbox"] > div > div {
            background-color: #161616;
            border-color: #252525;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str = "") -> None:
    """Render a styled page header — replaces st.title() on all pages."""
    sub_html = (
        f'<p style="font-family:Inter,sans-serif;font-size:0.82rem;'
        f'font-weight:300;color:#555;margin:0.4rem 0 0;line-height:1.5;">'
        f'{subtitle}</p>'
        if subtitle else ""
    )
    st.markdown(
        f'<div style="padding:1.4rem 0 1.1rem;border-bottom:2px solid #E8002D;margin-bottom:1.6rem;">'
        f'<div style="font-family:Inter,sans-serif;font-size:clamp(1.5rem,3vw,2.1rem);'
        f'font-weight:900;color:#FFFFFF;letter-spacing:-0.025em;line-height:1;">'
        f'{title}</div>{sub_html}</div>',
        unsafe_allow_html=True,
    )


def section_label(text: str) -> None:
    """Small uppercase section heading — replaces st.subheader()."""
    st.markdown(
        f'<div style="font-family:Inter,sans-serif;font-size:0.58rem;font-weight:700;'
        f'color:#3A3A3A;text-transform:uppercase;letter-spacing:0.2em;'
        f'margin:1.6rem 0 0.9rem;">{text}</div>',
        unsafe_allow_html=True,
    )


def divider() -> None:
    """Thin dark divider — replaces st.markdown('---')."""
    st.markdown(
        '<div style="height:1px;background:#1A1A1A;margin:1.4rem 0;"></div>',
        unsafe_allow_html=True,
    )
