import plotly.express as px
import streamlit as st

from utils.bigquery import query, table

st.set_page_config(page_title="Championship Battle", page_icon="📈", layout="wide")
st.title("📈 Driver Championship Battle")

season = st.selectbox("Season", [2024], index=0)
top_n = st.slider("Show top N drivers", min_value=3, max_value=10, value=5)

with st.spinner("Loading championship data..."):
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
        select
            round_number,
            event_name,
            driver_name,
            cumulative_points,
            championship_position
        from {table('mart_driver_standings')}
        where season = {season}
          and driver_name in ({driver_list})
        order by round_number, championship_position
    """)

fig = px.line(
    progression,
    x="round_number",
    y="cumulative_points",
    color="driver_name",
    markers=True,
    labels={
        "round_number": "Round",
        "cumulative_points": "Cumulative Points",
        "driver_name": "Driver",
    },
    title=f"{season} Driver Championship — Top {top_n}",
    hover_data=["event_name", "championship_position"],
)
fig.update_layout(
    xaxis=dict(tickmode="linear", dtick=1),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=500,
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("Points per Round")

points_per_round = query(f"""
    select
        round_number,
        event_name,
        driver_name,
        points_this_round
    from {table('mart_driver_standings')}
    where season = {season}
      and driver_name in ({driver_list})
    order by round_number, driver_name
""")

fig2 = px.bar(
    points_per_round,
    x="round_number",
    y="points_this_round",
    color="driver_name",
    barmode="group",
    labels={
        "round_number": "Round",
        "points_this_round": "Points Scored",
        "driver_name": "Driver",
    },
    hover_data=["event_name"],
    title=f"{season} Points Scored Each Round — Top {top_n}",
)
fig2.update_layout(
    xaxis=dict(tickmode="linear", dtick=1),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=400,
)
st.plotly_chart(fig2, use_container_width=True)
