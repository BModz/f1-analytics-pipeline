import streamlit as st
from utils.bigquery import query, table
from utils.styles import inject_css, page_header, section_label, divider, render_podium, f1_table, TEAM_COLOURS

st.set_page_config(page_title="Race Results — F1 Analytics", layout="wide")
inject_css()

page_header("Race Results", "Circuit-by-circuit breakdown for every round")

season = st.selectbox("Season", [2024], index=0, label_visibility="collapsed")

with st.spinner("Loading races..."):
    races = query(f"""
        select distinct round_number, event_name, circuit, country
        from {table('mart_race_results')}
        where season = {season}
        order by round_number
    """)

race_options = {
    f"Round {int(r['round_number'])}  ·  {r['event_name']}": int(r["round_number"])
    for _, r in races.iterrows()
}
selected_label = st.selectbox("Race", list(race_options.keys()))
selected_round = race_options[selected_label]

with st.spinner("Loading results..."):
    results = query(f"""
        select
            finish_position         as pos,
            driver_name,
            driver_nationality,
            team_name,
            grid_position           as grid,
            positions_gained,
            points,
            status,
            did_not_finish
        from {table('mart_race_results')}
        where season = {season} and round_number = {selected_round}
        order by finish_position
    """)

# ── Race podium ───────────────────────────────────────────────────────────────
podium_rows = results[~results["did_not_finish"].astype(bool)]
if len(podium_rows) >= 3:
    p1r = podium_rows[podium_rows["pos"] == 1].iloc[0]
    p2r = podium_rows[podium_rows["pos"] == 2].iloc[0] if len(podium_rows[podium_rows["pos"] == 2]) else podium_rows.iloc[1]
    p3r = podium_rows[podium_rows["pos"] == 3].iloc[0] if len(podium_rows[podium_rows["pos"] == 3]) else podium_rows.iloc[2]
    render_podium(
        p1={"name": p1r["driver_name"], "sub": p1r["team_name"], "value": f'{int(p1r["points"])} pts'},
        p2={"name": p2r["driver_name"], "sub": p2r["team_name"], "value": f'{int(p2r["points"])} pts'},
        p3={"name": p3r["driver_name"], "sub": p3r["team_name"], "value": f'{int(p3r["points"])} pts'},
    )
    divider()

# ── Summary metrics ───────────────────────────────────────────────────────────
dnf_count = int(results["did_not_finish"].astype(bool).sum())
total_pts_awarded = int(results["points"].sum())
fastest_gainer = results.sort_values("positions_gained", ascending=False).iloc[0]

col1, col2, col3 = st.columns(3)
col1.metric("Retirements", dnf_count)
col2.metric("Points Awarded", total_pts_awarded)
col3.metric("Most Positions Gained", fastest_gainer["driver_name"], f'+{int(fastest_gainer["positions_gained"])}')

divider()
section_label("Race Classification")

# ── Results table ─────────────────────────────────────────────────────────────
rows = ""
for _, row in results.iterrows():
    dnf = bool(row["did_not_finish"])
    pos_val = "DNF" if dnf else int(row["pos"])
    medal = f"medal-{int(row['pos'])}" if not dnf and int(row["pos"]) <= 3 else ""
    team_color = TEAM_COLOURS.get(row["team_name"], "#444")
    try:
        gained = int(row["positions_gained"])
    except (ValueError, TypeError):
        gained = 0
    if gained > 0:
        gain_html = f'<span class="gain-pos">&#9650; +{gained}</span>'
    elif gained < 0:
        gain_html = f'<span class="gain-neg">&#9660; {gained}</span>'
    else:
        gain_html = '<span class="gain-neu">—</span>'
    status_cls = "status-fin" if row["status"] == "Finished" else "status-dnf"
    pts = int(row["points"]) if not dnf else "—"
    rows += (
        f'<tr>'
        f'<td class="td-pos {medal}">{pos_val}</td>'
        f'<td class="td-main">{row["driver_name"]}<span class="td-sub">{row["driver_nationality"]}</span></td>'
        f'<td><span class="td-dot" style="background:{team_color}"></span>{row["team_name"]}</td>'
        f'<td style="color:#aaa">{int(row["grid"])}</td>'
        f'<td>{gain_html}</td>'
        f'<td class="td-main">{pts}</td>'
        f'<td><span class="{status_cls}">{row["status"]}</span></td>'
        f'</tr>'
    )

f1_table(["Pos", "Driver", "Constructor", "Grid", "+/−", "Points", "Status"], rows)
