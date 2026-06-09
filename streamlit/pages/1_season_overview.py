import streamlit as st
from utils.bigquery import query, table
from utils.styles import inject_css

st.set_page_config(page_title="Season Overview — F1 Analytics", layout="wide")
inject_css()

st.title("Season Overview")

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

    podiums = query(f"""
        select driver_name, count(*) as podiums
        from {table('mart_race_results')}
        where season = {season} and is_podium = true
        group by driver_name order by podiums desc limit 1
    """)

    dnf_leader = query(f"""
        select driver_name, count(*) as dnfs
        from {table('mart_race_results')}
        where season = {season} and did_not_finish = true
        group by driver_name order by dnfs desc limit 1
    """)

champion = final_standings.iloc[0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("World Champion", champion["driver_name"])
col2.metric("Champion Points", int(champion["points"]))
col3.metric(
    "Most Race Wins",
    race_wins.iloc[0]["driver_name"],
    f"{int(race_wins.iloc[0]['wins'])} wins",
)
col4.metric(
    "Most Podiums",
    podiums.iloc[0]["driver_name"],
    f"{int(podiums.iloc[0]['podiums'])} podiums",
)

st.markdown("---")
st.subheader("Driver Championship — Final Standings")

standings_display = final_standings.copy()
standings_display.columns = ["Pos", "Driver", "Nationality", "Code", "Points", "Wins"]
standings_display["Pos"] = standings_display["Pos"].astype(int)
standings_display["Points"] = standings_display["Points"].astype(int)
standings_display["Wins"] = standings_display["Wins"].astype(int)

st.dataframe(
    standings_display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Pos": st.column_config.NumberColumn(width="small"),
        "Points": st.column_config.NumberColumn(width="small"),
        "Wins": st.column_config.NumberColumn(width="small"),
        "Code": st.column_config.TextColumn(width="small"),
    },
)
