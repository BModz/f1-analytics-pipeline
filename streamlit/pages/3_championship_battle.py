import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from utils.bigquery import query, table
from utils.styles import inject_css, PLOTLY_LAYOUT, F1_RED

st.set_page_config(page_title="Championship Battle — F1 Analytics", layout="wide")
inject_css()

st.title("Driver Championship")

col_left, col_right = st.columns([3, 1])
with col_left:
    season = st.selectbox("Season", [2024], index=0, label_visibility="collapsed")
with col_right:
    top_n = st.slider("Drivers", min_value=3, max_value=10, value=5)

with st.spinner("Loading..."):
    top_drivers = query(f"""
        select driver_name
        from {table('mart_driver_standings')}
        where season = {season}
          and round_number = (
              select max(round_number)
              from {table('mart_driver_standings')}
              where season = {season}
          )
        order by championship_position
        limit {top_n}
    """)

    driver_list = ", ".join(f"'{d}'" for d in top_drivers["driver_name"].tolist())

    progression = query(f"""
        select round_number, event_name, driver_name, cumulative_points, championship_position
        from {table('mart_driver_standings')}
        where season = {season} and driver_name in ({driver_list})
        order by round_number, championship_position
    """)

    points_per_round = query(f"""
        select round_number, event_name, driver_name, points_this_round
        from {table('mart_driver_standings')}
        where season = {season} and driver_name in ({driver_list})
        order by round_number, driver_name
    """)

fig = px.line(
    progression,
    x="round_number",
    y="cumulative_points",
    color="driver_name",
    markers=True,
    labels={"round_number": "Round", "cumulative_points": "Points", "driver_name": "Driver"},
    hover_data=["event_name", "championship_position"],
)
fig.update_traces(line=dict(width=2.5), marker=dict(size=6))
fig.update_layout(
    **PLOTLY_LAYOUT,
    height=460,
    title=dict(text=f"{season} Championship — Cumulative Points", font=dict(size=16)),
)
fig.update_xaxes(tickmode="linear", dtick=1, gridcolor="#2A2A2A")
fig.update_yaxes(gridcolor="#2A2A2A")
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("Points Scored Per Round")

fig2 = px.bar(
    points_per_round,
    x="round_number",
    y="points_this_round",
    color="driver_name",
    barmode="group",
    labels={"round_number": "Round", "points_this_round": "Points", "driver_name": "Driver"},
    hover_data=["event_name"],
)
fig2.update_layout(
    **PLOTLY_LAYOUT,
    height=360,
    title=dict(text="Points Per Round", font=dict(size=16)),
)
fig2.update_xaxes(tickmode="linear", dtick=1, gridcolor="#2A2A2A")
fig2.update_yaxes(gridcolor="#2A2A2A")
st.plotly_chart(fig2, use_container_width=True)
