import plotly.express as px
import streamlit as st

from utils.bigquery import query, table

st.set_page_config(page_title="Driver Profile", page_icon="👤", layout="wide")
st.title("👤 Driver Profile")

season = st.selectbox("Season", [2024], index=0)

with st.spinner("Loading drivers..."):
    drivers = query(f"""
        select distinct driver_name, driver_nationality
        from {table('mart_race_results')}
        where season = {season}
        order by driver_name
    """)

selected_driver = st.selectbox("Driver", drivers["driver_name"].tolist())

with st.spinner(f"Loading {selected_driver}'s season..."):
    results = query(f"""
        select
            round_number,
            event_name,
            team_name,
            finish_position,
            grid_position,
            positions_gained,
            points,
            status,
            is_podium,
            is_winner,
            did_not_finish
        from {table('mart_race_results')}
        where season = {season}
          and driver_name = '{selected_driver}'
        order by round_number
    """)

    nationality = drivers[drivers["driver_name"] == selected_driver]["driver_nationality"].iloc[0]

wins = int(results["is_winner"].sum())
podiums = int(results["is_podium"].sum())
total_points = float(results["points"].sum())
avg_finish = float(results[~results["did_not_finish"]]["finish_position"].mean())
dnfs = int(results["did_not_finish"].sum())

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Nationality", nationality)
col2.metric("Race Wins", wins)
col3.metric("Podiums", podiums)
col4.metric("Total Points", int(total_points))
col5.metric("DNFs", dnfs)

st.markdown("---")

fig = px.bar(
    results,
    x="round_number",
    y="points",
    text="points",
    labels={"round_number": "Round", "points": "Points"},
    title=f"{selected_driver} — Points per Race ({season})",
    hover_data=["event_name", "finish_position", "status"],
    color="points",
    color_continuous_scale="Reds",
)
fig.update_traces(textposition="outside")
fig.update_layout(
    xaxis=dict(tickmode="linear", dtick=1),
    coloraxis_showscale=False,
    height=400,
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("Race-by-Race Breakdown")

display = results[["round_number", "event_name", "team_name", "grid_position",
                    "finish_position", "positions_gained", "points", "status"]].copy()
display.columns = ["Round", "Race", "Team", "Grid", "Finish", "Pos Gained", "Points", "Status"]
display["Round"] = display["Round"].astype(int)
display["Grid"] = display["Grid"].astype(int)
display["Finish"] = display["Finish"].astype(int)

st.dataframe(display, use_container_width=True, hide_index=True)
