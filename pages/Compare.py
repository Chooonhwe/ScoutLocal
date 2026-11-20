
from pathlib import Path

import pandas as pd
import streamlit as st

from scoutlocal.metrics.profiles import SCOUTING_PROFILES
from scoutlocal.ui.comparison_chart import render_comparison_radar
from scoutlocal.ui.metric_glossary import render_metric_glossary
from scoutlocal.ui.comparison_insights import (
    render_comparison_insights,
)

from scoutlocal.ui.view_mode import (
    render_view_mode,
    is_beginner_mode,
)

# configure comparison page
st.set_page_config(
    page_title="ScoutLocal | Compare",
    page_icon="⚔️",
    layout="wide",
)

DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "player_metrics_with_positions.csv"
)

MIN_MINUTES = 900


@st.cache_data
def load_players():
    return pd.read_csv(DATA_PATH)


def metric_label(metric):
    return metric.removesuffix("_per90").replace("_", " ").title()


# prepare percentile metrics for a selected player
def build_metrics(player, reference, metric_names):
    results = []

    for metric in metric_names:
        if metric not in reference.columns:
            continue

        if pd.isna(player[metric]):
            continue

        ranks = (
            reference[metric]
            .rank(method="average", pct=True)
            .mul(100)
        )

        percentile = ranks.get(player.name)

        results.append({
            "metric": metric,
            "value": float(player[metric]),
            "percentile": (
                float(percentile)
                if pd.notna(percentile)
                else None
            ),
        })

    return results


# page heading
st.title("⚔️ Player Comparison")

# let users choose their preferred explanation level
render_view_mode()

st.caption(
    "Compare footballers using position-specific statistics "
    "and percentile rankings."
)

st.divider()


# load eligible player records
try:
    df = load_players()
except FileNotFoundError:
    st.error(f"Player dataset not found: {DATA_PATH}")
    st.stop()

eligible = df[
    (df["minutes"] >= MIN_MINUTES)
    & df["primary_position_group"].isin(
        SCOUTING_PROFILES.keys()
    )
].copy()

if len(eligible) < 2:
    st.warning("Not enough eligible players for comparison.")
    st.stop()


# create searchable player labels
eligible["player_label"] = (
    eligible["player_name"].astype(str)
    + " | "
    + eligible["team_name"].astype(str)
    + " | "
    + eligible["primary_position_group"].astype(str)
)


# select first player
st.subheader("Select Players")

left_col, right_col = st.columns(2)

with left_col:
    first_index = st.selectbox(
        "Player A",
        options=eligible.index.tolist(),
        index=None,
        placeholder="Search first player...",
        format_func=lambda i: eligible.loc[i, "player_label"],
    )


# select a compatible second player
if first_index is None:
    st.info("Search and select Player A to begin comparing.")
    st.stop()

player_a = eligible.loc[first_index]
position = player_a["primary_position_group"]

comparison_pool = eligible[
    (eligible["primary_position_group"] == position)
    & ~(
        (eligible["player_id"] == player_a["player_id"])
        & (eligible["team_id"] == player_a["team_id"])
    )
].copy()

with right_col:
    second_index = st.selectbox(
        "Player B",
        options=comparison_pool.index.tolist(),
        index=None,
        placeholder="Search comparison player...",
        format_func=lambda i: comparison_pool.loc[
            i, "player_label"
        ],
        key=f"compare_b_{first_index}",
        disabled=comparison_pool.empty,
    )

if second_index is None:
    st.info("Select another player in the same positional group.")
    st.stop()

player_b = comparison_pool.loc[second_index]


# build positional peer reference group
reference = eligible[
    eligible["primary_position_group"] == position
].copy()

metric_names = SCOUTING_PROFILES[position]

metrics_a = build_metrics(player_a, reference, metric_names)
metrics_b = build_metrics(player_b, reference, metric_names)


# comparison summary cards
st.divider()

left_col, right_col = st.columns(2)

with left_col:
    with st.container(border=True):
        st.subheader(player_a["player_name"])
        st.caption(
            f"{player_a['team_name']} | {position}"
        )
        st.metric(
            "Minutes Played",
            f"{player_a['minutes']:,.2f}",
        )

with right_col:
    with st.container(border=True):
        st.subheader(player_b["player_name"])
        st.caption(
            f"{player_b['team_name']} | {position}"
        )
        st.metric(
            "Minutes Played",
            f"{player_b['minutes']:,.2f}",
        )


# organize the comparison
radar_tab, metrics_tab, insights_tab, glossary_tab = st.tabs(
    [
        "Radar Comparison",
        "Statistical Comparison",
        "Scouting Insights",
        "Learn the Metrics",
    ]
)


with radar_tab:
    st.subheader("Positional Radar Comparison")

    render_comparison_radar(
        metrics_a=metrics_a,
        metrics_b=metrics_b,
        player_a_name=player_a["player_name"],
        player_b_name=player_b["player_name"],
    )

    st.caption(
        f"Reference group: {len(reference)} eligible "
        f"{position} player-team records."
    )


with metrics_tab:
    st.subheader("Performance Comparison")

    player_b_metrics = {
        item["metric"]: item
        for item in metrics_b
    }

    rows = []

    for item in metrics_a:
        other = player_b_metrics.get(item["metric"])

        if other is None:
            continue

        rows.append({
            "Metric": metric_label(item["metric"]),
            "Player A /90": item["value"],
            "Player B /90": other["value"],
            "Player A Percentile": item["percentile"],
            "Player B Percentile": other["percentile"],
        })

    if rows:
        results = pd.DataFrame(rows)

        numeric_cols = results.select_dtypes(
            include="number"
        ).columns

        st.dataframe(
            results.style.format({
                col: "{:.2f}"
                for col in numeric_cols
            }),
            hide_index=True,
            use_container_width=True,
        )

        st.caption(
            f"Player A: {player_a['player_name']} | "
            f"Player B: {player_b['player_name']}"
        )
    else:
        st.info("No comparable statistics are available.")


# display comparison insights based on user experience level
with insights_tab:

    if is_beginner_mode():
        st.subheader("Understanding the Comparison")

        st.write(
            "This section explains how the two players "
            "differ using simple football language."
        )

        # match both players' statistics
        lookup_b = {
            item["metric"]: item
            for item in metrics_b
        }

        for item_a in metrics_a:
            metric = item_a["metric"]
            item_b = lookup_b.get(metric)

            if item_b is None:
                continue

            value_a = item_a.get("value")
            value_b = item_b.get("value")

            if value_a is None or value_b is None:
                continue

            if pd.isna(value_a) or pd.isna(value_b):
                continue

            name = metric_label(metric)

            with st.container(border=True):
                st.markdown(f"### {name}")

                left, right = st.columns(2)

                with left:
                    st.metric(
                        str(player_a["player_name"]),
                        f"{float(value_a):.2f} /90",
                    )

                with right:
                    st.metric(
                        str(player_b["player_name"]),
                        f"{float(value_b):.2f} /90",
                    )

                if float(value_a) > float(value_b):
                    st.write(
                        f"**{player_a['player_name']}** records "
                        f"more {name.lower()} per 90 minutes."
                    )

                elif float(value_b) > float(value_a):
                    st.write(
                        f"**{player_b['player_name']}** records "
                        f"more {name.lower()} per 90 minutes."
                    )

                else:
                    st.write(
                        "Both players record the same "
                        "amount of activity in this metric."
                    )

        st.info(
            "Per 90 minutes means statistics are adjusted "
            "to represent 90 minutes of playing time. "
            "Higher numbers do not always mean a better player."
        )

    else:
        # preserve the full technical scouting analysis
        render_comparison_insights(
            metrics_a=metrics_a,
            metrics_b=metrics_b,
            player_a_name=str(player_a["player_name"]),
            player_b_name=str(player_b["player_name"]),
        )


# explain the scouting metrics used in this comparison
with glossary_tab:
    st.write(
        "New to football analytics? Explore the terms "
        "used to compare these players."
    )

    shared_metrics = [
        metric
        for metric in SCOUTING_PROFILES[position]
        if metric in {
            item["metric"] for item in metrics_a
        }
        and metric in {
            item["metric"] for item in metrics_b
        }
    ]

    render_metric_glossary(shared_metrics)


# methodology
st.divider()

st.caption(
    "Percentiles are calculated within the same positional "
    "group using players with at least 900 minutes. "
    "Higher statistical activity does not always indicate "
    "better footballing ability."
)

st.caption("ScoutLocal | Player Comparison")
