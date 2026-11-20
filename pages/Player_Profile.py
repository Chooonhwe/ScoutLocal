
from pathlib import Path

import pandas as pd
import streamlit as st

from scoutlocal.metrics.profiles import SCOUTING_PROFILES
from scoutlocal.ui.player_header import render_player_header
from scoutlocal.ui.radar_chart import render_radar_chart
from scoutlocal.ui.metrics_card import (
    render_player_metrics,
    render_metric_breakdown,
)
from scoutlocal.ui.scouting_insights import render_scouting_insights
from scoutlocal.ui.metric_glossary import render_metric_glossary

# configure player profile page
st.set_page_config(
    page_title="ScoutLocal | Player Profile",
    page_icon="⚽",
    layout="wide",
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "player_metrics_with_positions.csv"
)

RANKING_MIN_MINUTES = 900


# load player dataset
@st.cache_data
def load_players():
    return pd.read_csv(DATA_PATH)


# calculate a player's scouting metrics and percentile ranks
def build_profile_metrics(player, reference, metrics):
    profile = []

    for metric in metrics:
        if metric not in player.index:
            continue

        value = player[metric]

        if pd.isna(value):
            continue

        percentile = None

        # only eligible players receive percentile rankings
        if (
            float(player["minutes"]) >= RANKING_MIN_MINUTES
            and metric in reference.columns
            and player.name in reference.index
        ):
            ranks = (
                reference[metric]
                .rank(method="average", pct=True)
                .mul(100)
            )

            rank = ranks.loc[player.name]

            if pd.notna(rank):
                percentile = float(rank)

        profile.append({
            "metric": metric,
            "value": float(value),
            "percentile": percentile,
        })

    return profile


# page title
st.title("Player Intelligence")

st.caption(
    "Explore individual player performance, positional "
    "benchmarks and evidence-based scouting insights."
)


# back navigation
if st.button("← Back to Discover"):
    st.switch_page("pages/Discover.py")


# retrieve selected player
player_id = st.session_state.get("selected_player_id")
team_id = st.session_state.get("selected_team_id")

if player_id is None or team_id is None:
    st.info(
        "No player selected. Open Discover and choose "
        "a player to view their scouting profile."
    )
    st.stop()


# load the dataset
try:
    players = load_players()
except FileNotFoundError:
    st.error(f"Player data not found: {DATA_PATH}")
    st.stop()


# match player and team together
matches = players[
    (players["player_id"] == int(player_id))
    & (players["team_id"] == int(team_id))
]

if matches.empty:
    st.warning(
        "The selected player could not be found. "
        "Please select another player from Discover."
    )
    st.stop()

player = matches.iloc[0]

player_name = str(player["player_name"])
position = str(player["primary_position_group"])
minutes = float(player["minutes"])


# find the player's positional scouting metrics
profile_metrics = SCOUTING_PROFILES.get(position, [])

# create the positional reference population
reference = players[
    (players["primary_position_group"] == position)
    & (players["minutes"] >= RANKING_MIN_MINUTES)
].copy()

# construct the player's statistical profile
metrics = build_profile_metrics(
    player,
    reference,
    profile_metrics,
)


# display the branded player header
render_player_header(
    player,
    competition="Indian Super League",
    season="2021/22",
)


# show primary statistical overview
render_player_metrics(
    player,
    peer_count=len(reference),
    metrics=metrics,
)




# organize the player analysis into four sections
overview_tab, breakdown_tab, insights_tab, academy_tab = st.tabs(
    [
        "Performance Overview",
        "Statistical Breakdown",
        "Scouting Intelligence",
        "Learn the Metrics",
    ]
)



# performance overview
with overview_tab:
    st.subheader("Positional Performance Radar")

    if minutes < RANKING_MIN_MINUTES:
        st.info(
            "The radar chart requires at least 900 "
            "recorded minutes to establish positional rankings."
        )
    else:
        render_radar_chart(
            metrics=metrics,
            player_name=player_name,
        )

    st.divider()

    st.subheader("Player Context")

    left_col, right_col = st.columns(2)

    with left_col:
        with st.container(border=True):
            st.caption("POSITIONAL GROUP")
            st.subheader(position)

            st.write(
                f"Compared against {len(reference)} "
                "eligible player-team records."
            )

    with right_col:
        with st.container(border=True):
            st.caption("DATA CONFIDENCE")

            if minutes >= RANKING_MIN_MINUTES:
                st.subheader("Ranking Eligible")
                st.write(
                    "Meets the 900-minute threshold "
                    "for positional percentile comparisons."
                )
            else:
                st.subheader("Limited Minutes")
                st.write(
                    "Per-90 statistics are available, "
                    "but percentile rankings are withheld."
                )


# statistical breakdown
with breakdown_tab:
    render_metric_breakdown(metrics)


# automated scouting insights
with insights_tab:
    render_scouting_insights(
        metrics=metrics,
        peer_count=len(reference),
    )


# explain the metrics used in this player's profile
with academy_tab:
    metric_names = [
        item["metric"]
        for item in metrics
    ]

    render_metric_glossary(metric_names)


# methodology
st.divider()

with st.expander("Scouting Methodology"):
    st.markdown(
        """
        **Statistical basis**

        - Statistics are calculated per 90 recorded minutes.
        - Positional comparisons use the Indian Super League 2021/22 dataset.
        - Players require at least 900 minutes for percentile eligibility.
        - Percentiles are calculated separately for each positional group.
        - Higher percentiles indicate higher recorded statistical activity,
          not necessarily greater overall football ability.
        - Player records are identified using both player ID and team ID.
        """
    )


# footer
st.caption(
    "ScoutLocal | Player Intelligence | StatsBomb Open Data"
)
