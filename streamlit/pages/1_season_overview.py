import streamlit as st
from utils.bigquery import query, table
from utils.styles import inject_css, page_header, section_label, divider, render_podium, f1_table

st.set_page_config(page_title="Season Overview — F1 Analytics", layout="wide")
inject_css()

page_header("Season Overview", "Final standings and season highlights — 2024")

season = st.selectbox("Season", [2024], index=0, label_visibility="collapsed")

with st.spinner("Loading..."):
    final_standings = query(f"""
        select
            championship_position   as pos,
            driver_name,
            driver_nationality,
            driver_code,
            cumulative_points       as points,
            cumulative_wins         as wins
        from {table('mart_driver_standings')}
        where season = {season}
          and round_number = (
              select max(round_number)
              from {table('mart_driver_standings')}
              where season = {season}
          )
        order by championship_position
    """)

    race_wins = query(f"""
        select driver_name, count(*) as wins
        from {table('mart_race_results')}
        where season = {season} and is_winner = true
        group by driver_name order by wins desc limit 1
    """)

    podiums_q = query(f"""
        select driver_name, count(*) as podiums
        from {table('mart_race_results')}
        where season = {season} and is_podium = true
        group by driver_name order by podiums desc limit 1
    """)

# ── Top-3 podium ──────────────────────────────────────────────────────────────
p1_row = final_standings[final_standings["pos"] == 1].iloc[0]
p2_row = final_standings[final_standings["pos"] == 2].iloc[0]
p3_row = final_standings[final_standings["pos"] == 3].iloc[0]

render_podium(
    p1={"name": p1_row["driver_name"], "sub": p1_row["driver_nationality"], "value": f'{int(p1_row["points"])} pts'},
    p2={"name": p2_row["driver_name"], "sub": p2_row["driver_nationality"], "value": f'{int(p2_row["points"])} pts'},
    p3={"name": p3_row["driver_name"], "sub": p3_row["driver_nationality"], "value": f'{int(p3_row["points"])} pts'},
)

divider()

# ── Season highlights ─────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("World Champion", p1_row["driver_name"], f'{int(p1_row["points"])} pts')
col2.metric(
    "Most Race Wins",
    race_wins.iloc[0]["driver_name"],
    f'{int(race_wins.iloc[0]["wins"])} wins',
)
col3.metric(
    "Most Podiums",
    podiums_q.iloc[0]["driver_name"],
    f'{int(podiums_q.iloc[0]["podiums"])} podiums',
)

divider()
section_label("Driver Championship — Final Standings")

# ── Standings table ───────────────────────────────────────────────────────────
max_pts = int(final_standings["points"].max())
rows = ""
for _, row in final_standings.iterrows():
    pos = int(row["pos"])
    medal = f"medal-{pos}" if pos <= 3 else ""
    pct = round(int(row["points"]) / max_pts * 100, 1)
    rows += (
        f'<tr>'
        f'<td class="td-pos {medal}">{pos}</td>'
        f'<td class="td-main">{row["driver_name"]}<span class="td-sub">{row["driver_code"]}</span></td>'
        f'<td>{row["driver_nationality"]}</td>'
        f'<td><div class="bar-cell"><div class="pts-bar-bg"><div class="pts-bar" style="width:{pct}%"></div></div>'
        f'<span class="pts-val">{int(row["points"])}</span></div></td>'
        f'<td class="td-main">{int(row["wins"])}</td>'
        f'</tr>'
    )

f1_table(["Pos", "Driver", "Nationality", "Points", "Wins"], rows)
