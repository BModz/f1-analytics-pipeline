import streamlit as st
from utils.bigquery import query, table
from utils.styles import inject_css, page_header, section_label, divider, F1_RED

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

winner = results[results["pos"] == 1].iloc[0]
p2 = results[results["pos"] == 2].iloc[0] if len(results) > 1 else None
p3 = results[results["pos"] == 3].iloc[0] if len(results) > 2 else None
dnf_count = int(results["did_not_finish"].sum())

col1, col2, col3, col4 = st.columns(4)
col1.metric("Winner", winner["driver_name"], winner["team_name"])
if p2 is not None:
    col2.metric("P2", p2["driver_name"], p2["team_name"])
if p3 is not None:
    col3.metric("P3", p3["driver_name"], p3["team_name"])
col4.metric("Retirements", dnf_count)

divider()
section_label("Classification")

display = results.drop(columns=["did_not_finish"]).copy()
display.columns = ["Pos", "Driver", "Nationality", "Team", "Grid", "Pos Gained", "Points", "Status"]
display["Pos"] = display["Pos"].astype(int)
display["Grid"] = display["Grid"].astype(int)
display["Points"] = display["Points"].astype(float)


def highlight_row(row):
    if row["Status"] != "Finished":
        return ["color: #555"] * len(row)
    elif row["Pos"] == 1:
        return [f"color: {F1_RED}; font-weight: 700"] * len(row)
    elif row["Pos"] <= 3:
        return ["font-weight: 600"] * len(row)
    return [""] * len(row)


st.dataframe(
    display.style.apply(highlight_row, axis=1),
    use_container_width=True,
    hide_index=True,
    column_config={
        "Pos": st.column_config.NumberColumn(width="small"),
        "Grid": st.column_config.NumberColumn(width="small"),
        "Points": st.column_config.NumberColumn(width="small"),
    },
)
