import plotly.graph_objects as go
import streamlit as st
from utils.bigquery import query, table
from utils.styles import inject_css, page_header, section_label, divider, f1_table, PLOTLY_LAYOUT, F1_RED, TEAM_COLOURS

st.set_page_config(page_title="Driver Profile — F1 Analytics", layout="wide")
inject_css()

page_header("Driver Profile", "Individual race results and performance trends")

col_left, col_right = st.columns([2, 2])
with col_left:
    season = st.selectbox("Season", [2024], index=0, label_visibility="collapsed")

with st.spinner("Loading drivers..."):
    drivers = query(f"""
        select distinct driver_name, driver_nationality
        from {table('mart_race_results')}
        where season = {season}
        order by driver_name
    """)

with col_right:
    selected_driver = st.selectbox("Driver", drivers["driver_name"].tolist(), label_visibility="collapsed")

with st.spinner("Loading season data..."):
    results = query(f"""
        select
            round_number, event_name, team_name,
            finish_position, grid_position, positions_gained,
            points, status, is_podium, is_winner, did_not_finish
        from {table('mart_race_results')}
        where season = {season}
          and driver_name = '{selected_driver}'
        order by round_number
    """)

nationality = drivers[drivers["driver_name"] == selected_driver]["driver_nationality"].iloc[0]
wins = int(results["is_winner"].sum())
podiums = int(results["is_podium"].sum())
total_points = int(results["points"].sum())
dnfs = int(results["did_not_finish"].sum())
finished = results[~results["did_not_finish"].astype(bool)]
avg_finish = round(float(finished["finish_position"].mean()), 1) if len(finished) else "—"

# ── Driver identity card ──────────────────────────────────────────────────────
primary_team = results["team_name"].value_counts().index[0] if len(results) > 0 else ""
team_color = TEAM_COLOURS.get(primary_team, F1_RED)

st.markdown(
    f'<div style="background:#161616;border:1px solid #1E1E1E;border-left:4px solid {team_color};'
    f'border-radius:6px;padding:1.3rem 1.6rem;margin-bottom:1.4rem;'
    f'display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem;">'
    f'<div><div style="font-family:Inter,sans-serif;font-size:1.75rem;font-weight:900;'
    f'color:#fff;letter-spacing:-0.025em;line-height:1;">{selected_driver}</div>'
    f'<div style="font-family:Inter,sans-serif;font-size:0.68rem;color:#383838;'
    f'font-weight:700;letter-spacing:0.12em;text-transform:uppercase;margin-top:0.3rem;">'
    f'{nationality} · {primary_team}</div></div>'
    f'<div style="display:flex;gap:2rem;flex-wrap:wrap;">'
    f'<div style="text-align:center;"><div style="font-family:Inter,sans-serif;font-size:1.5rem;'
    f'font-weight:900;color:{team_color};line-height:1;">{wins}</div>'
    f'<div style="font-family:Inter,sans-serif;font-size:0.56rem;color:#2E2E2E;'
    f'text-transform:uppercase;letter-spacing:0.14em;font-weight:700;margin-top:3px;">Wins</div></div>'
    f'<div style="text-align:center;"><div style="font-family:Inter,sans-serif;font-size:1.5rem;'
    f'font-weight:900;color:{team_color};line-height:1;">{podiums}</div>'
    f'<div style="font-family:Inter,sans-serif;font-size:0.56rem;color:#2E2E2E;'
    f'text-transform:uppercase;letter-spacing:0.14em;font-weight:700;margin-top:3px;">Podiums</div></div>'
    f'<div style="text-align:center;"><div style="font-family:Inter,sans-serif;font-size:1.5rem;'
    f'font-weight:900;color:{team_color};line-height:1;">{total_points}</div>'
    f'<div style="font-family:Inter,sans-serif;font-size:0.56rem;color:#2E2E2E;'
    f'text-transform:uppercase;letter-spacing:0.14em;font-weight:700;margin-top:3px;">Points</div></div>'
    f'<div style="text-align:center;"><div style="font-family:Inter,sans-serif;font-size:1.5rem;'
    f'font-weight:900;color:#333;line-height:1;">{dnfs}</div>'
    f'<div style="font-family:Inter,sans-serif;font-size:0.56rem;color:#2E2E2E;'
    f'text-transform:uppercase;letter-spacing:0.14em;font-weight:700;margin-top:3px;">DNFs</div></div>'
    f'<div style="text-align:center;"><div style="font-family:Inter,sans-serif;font-size:1.5rem;'
    f'font-weight:900;color:#555;line-height:1;">{avg_finish}</div>'
    f'<div style="font-family:Inter,sans-serif;font-size:0.56rem;color:#2E2E2E;'
    f'text-transform:uppercase;letter-spacing:0.14em;font-weight:700;margin-top:3px;">Avg Finish</div></div>'
    f'</div></div>',
    unsafe_allow_html=True,
)

# ── Points per race bar chart ─────────────────────────────────────────────────
section_label("Points per Race")

team_colour_map = {t: TEAM_COLOURS.get(t, "#555") for t in results["team_name"].unique()}
bar_colours = results["team_name"].map(team_colour_map).tolist()

fig = go.Figure()
fig.add_trace(go.Bar(
    x=results["round_number"],
    y=results["points"],
    marker_color=bar_colours,
    marker_line_width=0,
    text=results["points"].apply(lambda v: str(int(v)) if int(v) > 0 else ""),
    textposition="outside",
    textfont=dict(size=10, color="#888"),
    customdata=results[["event_name", "finish_position", "status", "team_name"]].values,
    hovertemplate=(
        "<b>Round %{x}</b> — %{customdata[0]}<br>"
        "Finish: P%{customdata[1]}<br>"
        "Status: %{customdata[2]}<br>"
        "Team: %{customdata[3]}<br>"
        "Points: %{y}<extra></extra>"
    ),
))
fig.update_layout(
    **PLOTLY_LAYOUT,
    height=380,
    title=dict(text=f"{selected_driver} — Points per Race ({season})", font=dict(size=14, color="#888")),
    showlegend=False,
)
fig.update_xaxes(tickmode="linear", dtick=1, gridcolor="#1A1A1A", title="Round")
fig.update_yaxes(gridcolor="#1A1A1A", title="Points")
st.plotly_chart(fig, use_container_width=True)

divider()
section_label("Finishing Positions")

dnf_rows = results[results["did_not_finish"].astype(bool)]

fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=finished["round_number"],
    y=finished["finish_position"],
    mode="lines+markers",
    name="Finish Position",
    line=dict(color=team_color, width=2.5),
    marker=dict(size=8, color=team_color, line=dict(width=1.5, color="#111")),
    customdata=finished[["event_name", "grid_position", "status"]].values,
    hovertemplate=(
        "<b>Round %{x}</b> — %{customdata[0]}<br>"
        "Finish: P%{y}<br>"
        "Grid: P%{customdata[1]}<extra></extra>"
    ),
))
if len(dnf_rows):
    fig2.add_trace(go.Scatter(
        x=dnf_rows["round_number"],
        y=[21] * len(dnf_rows),
        mode="markers",
        name="DNF",
        marker=dict(symbol="x-thin", size=14, color="#3A3A3A", line=dict(width=2.5, color="#3A3A3A")),
        customdata=dnf_rows[["event_name", "status"]].values,
        hovertemplate=(
            "<b>Round %{x}</b> — %{customdata[0]}<br>"
            "Status: %{customdata[1]}<extra></extra>"
        ),
    ))
fig2.update_layout(
    **PLOTLY_LAYOUT,
    height=340,
    title=dict(text="Finishing Positions", font=dict(size=14, color="#888")),
)
fig2.update_xaxes(tickmode="linear", dtick=1, gridcolor="#1A1A1A", title="Round")
fig2.update_yaxes(
    autorange="reversed",
    gridcolor="#1A1A1A",
    title="Finish Position",
    tickvals=list(range(1, 21, 2)),
)
st.plotly_chart(fig2, use_container_width=True)

divider()
section_label("Race-by-Race Breakdown")

rows = ""
for _, row in results.iterrows():
    dnf = bool(row["did_not_finish"])
    pos_val = "DNF" if dnf else int(row["finish_position"])
    medal = f"medal-{int(row['finish_position'])}" if not dnf and int(row["finish_position"]) <= 3 else ""
    team_c = TEAM_COLOURS.get(row["team_name"], "#555")
    try:
        gained = int(row["positions_gained"])
    except (ValueError, TypeError):
        gained = 0
    gain_html = (
        f'<span class="gain-pos">+{gained}</span>' if gained > 0
        else f'<span class="gain-neg">{gained}</span>' if gained < 0
        else '<span class="gain-neu">—</span>'
    )
    status_cls = "status-fin" if row["status"] == "Finished" else "status-dnf"
    pts = int(row["points"]) if not dnf else "—"
    rows += (
        f'<tr>'
        f'<td style="color:#444;font-size:0.78rem;">{int(row["round_number"])}</td>'
        f'<td class="td-main">{row["event_name"]}</td>'
        f'<td><span class="td-dot" style="background:{team_c}"></span>{row["team_name"]}</td>'
        f'<td style="color:#aaa">{int(row["grid_position"])}</td>'
        f'<td class="td-pos {medal}">{pos_val}</td>'
        f'<td>{gain_html}</td>'
        f'<td class="td-main">{pts}</td>'
        f'<td><span class="{status_cls}">{row["status"]}</span></td>'
        f'</tr>'
    )

f1_table(["Rnd", "Race", "Constructor", "Grid", "Finish", "+/−", "Points", "Status"], rows)
