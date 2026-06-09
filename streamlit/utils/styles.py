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
    xaxis=dict(gridcolor="#1A1A1A", linecolor="#1A1A1A"),
    yaxis=dict(gridcolor="#1A1A1A", linecolor="#1A1A1A"),
    legend=dict(
        bgcolor="#161616",
        bordercolor="#1E1E1E",
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

        .block-container { padding-top: 1.2rem; padding-bottom: 1rem; }
        html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
        h1 { border-bottom: 2px solid #E8002D; padding-bottom: 0.4rem; margin-bottom: 1.2rem; }

        [data-testid="metric-container"] {
            background-color: #161616;
            border: 1px solid #1E1E1E;
            border-left: 3px solid #E8002D;
            border-radius: 4px;
            padding: 1rem 1.2rem;
        }
        [data-testid="stMetricLabel"] { color: #555 !important; font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }
        [data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 1.5rem; font-weight: 700; }
        [data-testid="stMetricDelta"] { font-size: 0.78rem; }

        hr { border-color: #1A1A1A; }
        .stDataFrame { border: 1px solid #1A1A1A; border-radius: 4px; }
        label { color: #777 !important; font-size: 0.8rem; }
        [data-testid="stSidebar"] { background-color: #0A0A0A; border-right: 1px solid #1A1A1A; }
        [data-testid="stSelectbox"] > div > div { background-color: #161616; border-color: #1E1E1E; }

        /* ── F1 TABLE ─────────────────────────────────── */
        .f1-table-wrap { border-radius: 6px; overflow: hidden; border: 1px solid #1A1A1A; margin-top: 0.4rem; }
        .f1-table { width: 100%; border-collapse: collapse; font-family: 'Inter', sans-serif; }
        .f1-table thead tr { background: #0C0C0C; }
        .f1-table thead th {
            padding: 0.6rem 1rem;
            font-size: 0.55rem;
            font-weight: 700;
            color: #2E2E2E;
            text-transform: uppercase;
            letter-spacing: 0.18em;
            text-align: left;
            border-bottom: 1px solid #161616;
            white-space: nowrap;
        }
        .f1-table tbody tr { border-bottom: 1px solid #101010; transition: background 0.12s; animation: rowfade 0.4s ease both; }
        .f1-table tbody tr:hover { background: #181818 !important; }
        .f1-table tbody tr:last-child { border-bottom: none; }
        .f1-table tbody td { padding: 0.65rem 1rem; font-size: 0.82rem; color: #777; vertical-align: middle; }
        .f1-table tbody tr:nth-child(even) { background: #131313; }
        @keyframes rowfade { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }

        .td-pos { font-family: 'Inter', sans-serif; font-weight: 800; font-size: 0.88rem; color: #fff !important; width: 2rem; text-align: center; }
        .medal-1 { color: #FFD700 !important; }
        .medal-2 { color: #C0C0C0 !important; }
        .medal-3 { color: #CD7F32 !important; }
        .td-main { font-weight: 600; color: #E8E8E8 !important; }
        .td-sub { font-size: 0.66rem; color: #383838; display: block; margin-top: 2px; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase; }
        .td-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 7px; vertical-align: middle; flex-shrink: 0; }

        .bar-cell { display: flex; align-items: center; gap: 0.6rem; min-width: 120px; }
        .pts-bar-bg { flex: 1; height: 3px; background: #1A1A1A; border-radius: 2px; overflow: hidden; }
        .pts-bar { height: 3px; background: #E8002D; border-radius: 2px; transform-origin: left; animation: barfill 1s cubic-bezier(0.22,1,0.36,1) both; }
        .pts-val { font-size: 0.85rem; color: #fff; font-weight: 700; white-space: nowrap; min-width: 2.5rem; text-align: right; }
        @keyframes barfill { from { transform: scaleX(0); } to { transform: scaleX(1); } }

        .status-fin { color: #3D9B3D; font-weight: 600; }
        .status-dnf { color: #404040; }
        .gain-pos { color: #3D9B3D; font-weight: 700; }
        .gain-neg { color: #E8002D; font-weight: 700; }
        .gain-neu { color: #333; }

        /* ── PODIUM ───────────────────────────────────── */
        .f1-podium { display: flex; align-items: flex-end; justify-content: center; gap: 2px; margin: 1.2rem 0 0; }
        .pod-slot { flex: 1; max-width: 210px; display: flex; flex-direction: column; align-items: center; }
        .pod-info { text-align: center; padding-bottom: 0.65rem; }
        .pod-num { font-family: 'Inter', sans-serif; font-size: 0.56rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.22em; margin-bottom: 0.22rem; }
        .pod-name { font-family: 'Inter', sans-serif; font-size: 0.92rem; font-weight: 700; color: #EFEFEF; line-height: 1.2; }
        .pod-sub { font-family: 'Inter', sans-serif; font-size: 0.68rem; color: #3A3A3A; margin-top: 0.15rem; }
        .pod-val { font-family: 'Inter', sans-serif; font-size: 1rem; font-weight: 900; margin-top: 0.22rem; }
        .pod-block { width: 100%; border-radius: 3px 3px 0 0; transform-origin: bottom; animation: podrise 0.7s cubic-bezier(0.22,1,0.36,1) both; }
        .pod1 .pod-num, .pod1 .pod-val { color: #FFD700; }
        .pod1 .pod-block { height: 120px; background: linear-gradient(180deg, #201E0A 0%, #141400 100%); border-top: 2px solid #FFD700; animation-delay: 0s; }
        .pod2 .pod-num, .pod2 .pod-val { color: #B8B8B8; }
        .pod2 .pod-block { height: 80px; background: linear-gradient(180deg, #1A1A1A 0%, #111 100%); border-top: 2px solid #B8B8B8; animation-delay: 0.1s; }
        .pod3 .pod-num, .pod3 .pod-val { color: #A0622A; }
        .pod3 .pod-block { height: 55px; background: linear-gradient(180deg, #1E1610 0%, #131010 100%); border-top: 2px solid #A0622A; animation-delay: 0.2s; }
        @keyframes podrise { from { transform: scaleY(0); } to { transform: scaleY(1); } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str = "") -> None:
    sub_html = (
        f'<p style="font-family:Inter,sans-serif;font-size:0.82rem;font-weight:300;'
        f'color:#484848;margin:0.4rem 0 0;line-height:1.5;">{subtitle}</p>'
        if subtitle else ""
    )
    st.markdown(
        f'<div style="padding:1.4rem 0 1.1rem;border-bottom:2px solid #E8002D;margin-bottom:1.6rem;">'
        f'<div style="font-family:Inter,sans-serif;font-size:clamp(1.5rem,3vw,2.1rem);'
        f'font-weight:900;color:#FFFFFF;letter-spacing:-0.025em;line-height:1;">{title}</div>'
        f'{sub_html}</div>',
        unsafe_allow_html=True,
    )


def section_label(text: str) -> None:
    st.markdown(
        f'<div style="font-family:Inter,sans-serif;font-size:0.56rem;font-weight:700;'
        f'color:#2E2E2E;text-transform:uppercase;letter-spacing:0.22em;margin:1.6rem 0 0.9rem;">'
        f'{text}</div>',
        unsafe_allow_html=True,
    )


def divider() -> None:
    st.markdown(
        '<div style="height:1px;background:#141414;margin:1.4rem 0;"></div>',
        unsafe_allow_html=True,
    )


def render_podium(p1: dict, p2: dict, p3: dict) -> None:
    """Animated F1 podium. Each dict: {name, sub, value}"""
    st.markdown(
        f'<div class="f1-podium">'
        f'<div class="pod-slot pod2"><div class="pod-info"><div class="pod-num">P2</div><div class="pod-name">{p2["name"]}</div><div class="pod-sub">{p2["sub"]}</div><div class="pod-val">{p2["value"]}</div></div><div class="pod-block"></div></div>'
        f'<div class="pod-slot pod1"><div class="pod-info"><div class="pod-num">P1</div><div class="pod-name">{p1["name"]}</div><div class="pod-sub">{p1["sub"]}</div><div class="pod-val">{p1["value"]}</div></div><div class="pod-block"></div></div>'
        f'<div class="pod-slot pod3"><div class="pod-info"><div class="pod-num">P3</div><div class="pod-name">{p3["name"]}</div><div class="pod-sub">{p3["sub"]}</div><div class="pod-val">{p3["value"]}</div></div><div class="pod-block"></div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def f1_table(headers: list, rows_html: str) -> None:
    """Render a styled F1 data table. rows_html: concatenated <tr>...</tr> strings."""
    ths = "".join(f"<th>{h}</th>" for h in headers)
    st.markdown(
        f'<div class="f1-table-wrap"><table class="f1-table">'
        f'<thead><tr>{ths}</tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        f'</table></div>',
        unsafe_allow_html=True,
    )
