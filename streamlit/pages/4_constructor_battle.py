import plotly.express as px
import streamlit as st
from utils.bigquery import query, table
from utils.styles import inject_css, page_header, section_label, divider, render_podium, f1_table, PLOTLY_LAYOUT, TEAM_COLOURS

st.set_page_config(page_title="Constructor Battle — F1 Analytics", layout="wide")
inject_css()

page_header("Constructor Championship", "Constructors' standings and cumulative points race")

season = st.selectbox("Season", [2024], index=0, label_visibility="collapsed")

with st.spinner("Loading..."):
    progression = query(f"""
        select
            round_number, event_name, constructor_name,
            cumulative_points, championship_position, points_this_round
        from {table('mart_constructor_standings')}
        where season = {season}
        order by round_number, championship_position
    """)

    final = query(f"""
        select
            championship_position   as pos,
            constructor_name,
            constructor_nationality,
            cumulative_points       as points,
            cumulative_wins         as wins
        from {table('mart_constructor_standings')}
        where season = {season}
          and round_number = (
              select max(round_number)
              from {table('mart_constructor_standings')}
              where season = {season}
          )
        order by championship_position
    """)

# ── Constructors' podium ──────────────────────────────────────────────────────
if len(final) >= 3:
    render_podium(
        p1={"name": final.iloc[0]["constructor_name"], "sub": final.iloc[0]["constructor_nationality"], "value": f'{int(final.iloc[0]["points"])} pts'},
        p2={"name": final.iloc[1]["constructor_name"], "sub": final.iloc[1]["constructor_nationality"], "value": f'{int(final.iloc[1]["points"])} pts'},
        p3={"name": final.iloc[2]["constructor_name"], "sub": final.iloc[2]["constructor_nationality"], "value": f'{int(final.iloc[2]["points"])} pts'},
    )
    divider()

# ── Gap metrics ───────────────────────────────────────────────────────────────
champion = final.iloc[0]
runner_up = final.iloc[1] if len(final) > 1 else None
gap = int(champion["points"]) - int(runner_up["points"]) if runner_up is not None else 0

col1, col2, col3 = st.columns(3)
col1.metric("Constructors' Champion", champion["constructor_name"], f'{int(champion["points"])} pts')
if runner_up is not None:
    col2.metric("Runner-Up", runner_up["constructor_name"], f'{int(runner_up["points"])} pts')
    col3.metric("Winning Margin", f"{gap} pts")

divider()
section_label("Cumulative Points Race")

colour_map = {name: TEAM_COLOURS.get(name, "#555") for name in progression["constructor_name"].unique()}

fig = px.line(
    progression,
    x="round_number",
    y="cumulative_points",
    color="constructor_name",
    color_discrete_map=colour_map,
    markers=True,
    labels={"round_number": "Round", "cumulative_points": "Points", "constructor_name": "Constructor"},
    hover_data=["event_name", "championship_position"],
)
fig.update_traces(line=dict(width=2.5), marker=dict(size=7))
fig.update_layout(
    **PLOTLY_LAYOUT,
    height=460,
    title=dict(text=f"{season} Constructors' Championship — Cumulative Points", font=dict(size=14, color="#888")),
)
fig.update_xaxes(tickmode="linear", dtick=1, gridcolor="#1A1A1A", title="Round")
fig.update_yaxes(gridcolor="#1A1A1A", title="Points")
st.plotly_chart(fig, use_container_width=True)

divider()
section_label("Final Standings")

max_pts = int(final["points"].max())
rows = ""
for _, row in final.iterrows():
    pos = int(row["pos"])
    medal = f"medal-{pos}" if pos <= 3 else ""
    team_color = TEAM_COLOURS.get(row["constructor_name"], "#555")
    pct = round(int(row["points"]) / max_pts * 100, 1)
    rows += (
        f'<tr>'
        f'<td class="td-pos {medal}">{pos}</td>'
        f'<td class="td-main"><span class="td-dot" style="background:{team_color}"></span>{row["constructor_name"]}'
        f'<span class="td-sub">{row["constructor_nationality"]}</span></td>'
        f'<td><div class="bar-cell"><div class="pts-bar-bg"><div class="pts-bar" style="width:{pct}%"></div></div>'
        f'<span class="pts-val">{int(row["points"])}</span></div></td>'
        f'<td class="td-main">{int(row["wins"])}</td>'
        f'</tr>'
    )

f1_table(["Pos", "Constructor", "Points", "Wins"], rows)
