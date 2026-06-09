import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from utils.bigquery import query, table
from utils.styles import inject_css, PLOTLY_LAYOUT, F1_RED, TEAM_COLOURS

st.set_page_config(page_title="Driver Profile — F1 Analytics", layout="wide")
inject_css()

st.title("Driver Profile")

col_left, col_right = st.columns([2, 2])
with col_left:
    season = st.selectbox("Season", [2024], index=0, label_visibility="collapsed")

with st.spinner("Loading drivers..."):
    drivers = query(f"""
        select distinct driver_name, driver_nationality
        from {table('mart_race_results')}
        where season = {season}
        order by driver_name
    """)

with col_right:
    selected_driver = st.selectbox("Driver", drivers["driver_name"].tolist(), label_visibility="collapsed")

with st.spinner("Loading season data..."):
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
total_points = int(results["points"].sum())
avg_finish = round(float(results[~results["did_not_finish"]]["finish_position"].mean()), 1)
dnfs = int(results["did_not_finish"].sum())

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Nationality", nationality)
col2.metric("Race Wins", wins)
col3.metric("Podiums", podiums)
col4.metric("Total Points", total_points)
col5.metric("DNFs", dnfs)

st.markdown("---")

# Points per race — colour each bar by team
team_colour_map = {t: TEAM_COLOURS.get(t, "#888888") for t in results["team_name"].unique()}
bar_colours = results["team_name"].map(team_colour_map).tolist()

fig = go.Figure()
fig.add_trace(go.Bar(
    x=results["round_number"],
    y=results["points"],
    marker_color=bar_colours,
    text=results["points"].astype(int),
    textposition="outside",
    customdata=results[["event_name", "finish_position", "status", "team_name"]].values,
    hovertemplate=(
        "<b>Round %{x}</b> — %{customdata[0]}<br>"
        "Finish: P%{customdata[1]}<br>"
        "Status: %{customdata[2]}<br>"
        "Team: %{customdata[3]}<br>"
        "Points: %{y}<extra></extra>"
    ),
))
fig.update_layout(
    **PLOTLY_LAYOUT,
    height=400,
    xaxis=dict(tickmode="linear", dtick=1, gridcolor="#2A2A2A", title="Round"),
    yaxis=dict(gridcolor="#2A2A2A", title="Points"),
    title=dict(text=f"{selected_driver} — Points per Race ({season})", font=dict(size=16)),
    showlegend=False,
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Finishing position scatter
fig2 = go.Figure()
finished = results[~results["did_not_finish"]]
dnf_rows = results[results["did_not_finish"]]

fig2.add_trace(go.Scatter(
    x=finished["round_number"],
    y=finished["finish_position"],
    mode="lines+markers",
    name="Finish Position",
    line=dict(color=F1_RED, width=2),
    marker=dict(size=8, color=F1_RED),
    customdata=finished[["event_name", "grid_position", "status"]].values,
    hovertemplate=(
        "<b>Round %{x}</b> — %{customdata[0]}<br>"
        "Finish: P%{y}<br>"
        "Grid: P%{customdata[1]}<extra></extra>"
    ),
))
if len(dnf_rows):
    fig2.add_trace(go.Scatter(
        x=dnf_rows["round_number"],
        y=[25] * len(dnf_rows),
        mode="markers",
        name="DNF",
        marker=dict(symbol="x", size=12, color="#888888"),
        customdata=dnf_rows[["event_name", "status"]].values,
        hovertemplate=(
            "<b>Round %{x}</b> — %{customdata[0]}<br>"
            "Status: %{customdata[1]}<extra></extra>"
        ),
    ))
fig2.update_layout(
    **PLOTLY_LAYOUT,
    height=360,
    xaxis=dict(tickmode="linear", dtick=1, gridcolor="#2A2A2A", title="Round"),
    yaxis=dict(autorange="reversed", gridcolor="#2A2A2A", title="Finish Position",
               tickvals=list(range(1, 21, 2))),
    title=dict(text="Finishing Positions", font=dict(size=16)),
)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.subheader("Race-by-Race Breakdown")

display = results[["round_number", "event_name", "team_name", "grid_position",
                    "finish_position", "positions_gained", "points", "status"]].copy()
display.columns = ["Round", "Race", "Team", "Grid", "Finish", "Pos Gained", "Points", "Status"]
display["Round"] = display["Round"].astype(int)
display["Grid"] = display["Grid"].astype(int)
display["Finish"] = display["Finish"].astype(int)
display["Points"] = display["Points"].astype(float)

def highlight_profile_row(row):
    if row["Status"] != "Finished":
        return ["color: #888888"] * len(row)
    elif row["Finish"] == 1:
        return [f"color: {F1_RED}; font-weight: 700"] * len(row)
    elif row["Finish"] <= 3:
        return ["font-weight: 600"] * len(row)
    return [""] * len(row)

st.dataframe(
    display.style.apply(highlight_profile_row, axis=1),
    use_container_width=True,
    hide_index=True,
    column_config={
        "Round": st.column_config.NumberColumn(width="small"),
        "Grid": st.column_config.NumberColumn(width="small"),
        "Finish": st.column_config.NumberColumn(width="small"),
        "Points": st.column_config.NumberColumn(width="small"),
    },
)
