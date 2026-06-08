import plotly.express as px
import streamlit as st

from utils.bigquery import query, table

st.set_page_config(page_title="Constructor Battle", page_icon="🏗️", layout="wide")
st.title("🏗️ Constructor Championship Battle")

season = st.selectbox("Season", [2024], index=0)

with st.spinner("Loading constructor data..."):
    progression = query(f"""
        select
            round_number,
            event_name,
            constructor_name,
            cumulative_points,
            championship_position,
            points_this_round
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

champion = final.iloc[0]
col1, col2 = st.columns(2)
col1.metric("Constructors' Champion", champion["constructor_name"])
col2.metric("Champion Points", int(champion["points"]))

st.markdown("---")

fig = px.line(
    progression,
    x="round_number",
    y="cumulative_points",
    color="constructor_name",
    markers=True,
    labels={
        "round_number": "Round",
        "cumulative_points": "Cumulative Points",
        "constructor_name": "Constructor",
    },
    title=f"{season} Constructors' Championship",
    hover_data=["event_name", "championship_position"],
)
fig.update_layout(
    xaxis=dict(tickmode="linear", dtick=1),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=500,
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("Final Standings")

final_display = final.copy()
final_display.columns = ["Pos", "Constructor", "Nationality", "Points", "Wins"]
final_display["Pos"] = final_display["Pos"].astype(int)
final_display["Points"] = final_display["Points"].astype(int)
final_display["Wins"] = final_display["Wins"].astype(int)

st.dataframe(final_display, use_container_width=True, hide_index=True)
