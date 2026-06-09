import plotly.express as px
import streamlit as st
from utils.bigquery import query, table
from utils.styles import inject_css, PLOTLY_LAYOUT, TEAM_COLOURS

st.set_page_config(page_title="Constructor Battle — F1 Analytics", layout="wide")
inject_css()

st.title("Constructor Championship")

season = st.selectbox("Season", [2024], index=0, label_visibility="collapsed")

with st.spinner("Loading..."):
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
runner_up = final.iloc[1] if len(final) > 1 else None
gap = int(champion["points"]) - int(runner_up["points"]) if runner_up is not None else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Constructors' Champion", champion["constructor_name"])
col2.metric("Champion Points", int(champion["points"]))
if runner_up is not None:
    col3.metric("Runner-Up", runner_up["constructor_name"])
    col4.metric("Gap", f"{gap} pts")

st.markdown("---")

colour_map = {name: TEAM_COLOURS.get(name, "#888888") for name in progression["constructor_name"].unique()}

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
fig.update_traces(line=dict(width=2.5), marker=dict(size=6))
fig.update_layout(
    **PLOTLY_LAYOUT,
    height=460,
    xaxis=dict(tickmode="linear", dtick=1, gridcolor="#2A2A2A"),
    yaxis=dict(gridcolor="#2A2A2A"),
    title=dict(text=f"{season} Constructors' Championship — Cumulative Points", font=dict(size=16)),
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("Final Standings")

final_display = final.copy()
final_display.columns = ["Pos", "Constructor", "Nationality", "Points", "Wins"]
final_display["Pos"] = final_display["Pos"].astype(int)
final_display["Points"] = final_display["Points"].astype(int)
final_display["Wins"] = final_display["Wins"].astype(int)

st.dataframe(
    final_display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Pos": st.column_config.NumberColumn(width="small"),
        "Points": st.column_config.NumberColumn(width="small"),
        "Wins": st.column_config.NumberColumn(width="small"),
    },
)
