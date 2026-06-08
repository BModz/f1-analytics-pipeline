import streamlit as st

from utils.bigquery import query, table

st.set_page_config(page_title="Race Results", page_icon="🏁", layout="wide")
st.title("🏁 Race Results")

season = st.selectbox("Season", [2024], index=0)

with st.spinner("Loading races..."):
    races = query(f"""
        select distinct round_number, event_name
        from {table('mart_race_results')}
        where season = {season}
        order by round_number
    """)

race_options = {
    f"Round {int(r['round_number'])} — {r['event_name']}": int(r["round_number"])
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
        where season = {season}
          and round_number = {selected_round}
        order by finish_position
    """)

col1, col2, col3 = st.columns(3)
winner = results[results["pos"] == 1].iloc[0]
col1.metric("Winner", winner["driver_name"])
col2.metric("Team", winner["team_name"])
dnf_count = int(results["did_not_finish"].sum())
col3.metric("DNFs", dnf_count)

st.markdown("---")

display = results.drop(columns=["did_not_finish"]).copy()
display.columns = ["Pos", "Driver", "Nationality", "Team", "Grid", "Pos Gained", "Points", "Status"]
display["Pos"] = display["Pos"].astype(int)
display["Grid"] = display["Grid"].astype(int)
display["Points"] = display["Points"].astype(float)

def highlight_dnf(row):
    if row["Status"] != "Finished":
        return ["background-color: #3d1a1a"] * len(row)
    elif row["Pos"] <= 3:
        return ["background-color: #1a3d1a"] * len(row)
    return [""] * len(row)

st.dataframe(
    display.style.apply(highlight_dnf, axis=1),
    use_container_width=True,
    hide_index=True,
)
