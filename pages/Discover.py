
from pathlib import Path

import pandas as pd
import streamlit as st

from scoutlocal.metrics.profiles import SCOUTING_PROFILES


# configure discovery page
st.set_page_config(
    page_title="ScoutLocal | Discover",
    page_icon="🔎",
    layout="wide",
)

DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "player_metrics_with_positions.csv"
)

MIN_MINUTES = 0
RANKING_MIN_MINUTES = 900


@st.cache_data
def load_players():
    return pd.read_csv(DATA_PATH)


def metric_label(metric):
    return metric.removesuffix("_per90").replace("_", " ").title()


# calculate percentiles within each positional group
@st.cache_data
def calculate_percentiles(players, metrics):
    ranked = players.copy()

    for metric in metrics:
        ranked[f"pct__{metric}"] = (
            ranked.groupby("primary_position_group")[metric]
            .rank(method="average", pct=True)
            .mul(100)
        )

    return ranked


# clear selected player when filters change
def reset_selection():
    st.session_state.pop("discover_player", None)


# page heading
st.title("🔎 Discover Players")

st.caption(
    "Discover football talent through positional, "
    "team and advanced statistical filters."
)

st.divider()


# load player dataset
try:
    df = load_players()
except FileNotFoundError:
    st.error(f"Data file not found: {DATA_PATH}")
    st.stop()


# keep eligible players with supported scouting profiles
# all players with supported positions can be discovered
eligible = df[
    df["primary_position_group"].isin(
        SCOUTING_PROFILES.keys()
    )
].copy()

# only players with sufficient minutes form percentile reference groups
ranking_pool = eligible[
    eligible["minutes"] >= RANKING_MIN_MINUTES
].copy()

if eligible.empty:
    st.warning("No eligible players found.")
    st.stop()


# create player labels
eligible["player_label"] = (
    eligible["player_name"].astype(str)
    + " | "
    + eligible["team_name"].astype(str)
    + " | ID "
    + eligible["player_id"].astype(str)
)


# sidebar filters
st.sidebar.header("Player Filters")

positions = ["All positions"] + sorted(
    eligible["primary_position_group"].unique().tolist()
)

selected_position = st.sidebar.selectbox(
    "Position",
    positions,
    key="discover_position",
    on_change=reset_selection,
)

position_pool = eligible.copy()

if selected_position != "All positions":
    position_pool = position_pool[
        position_pool["primary_position_group"]
        == selected_position
    ]


# filter available teams based on position
teams = ["All teams"] + sorted(
    position_pool["team_name"].dropna().unique().tolist()
)

if st.session_state.get("discover_team") not in teams:
    st.session_state["discover_team"] = "All teams"

selected_team = st.sidebar.selectbox(
    "Team",
    teams,
    key="discover_team",
    on_change=reset_selection,
)

minimum_minutes = st.sidebar.number_input(
    "Minimum minutes played",
    min_value=MIN_MINUTES,
    value=MIN_MINUTES,
    step=100,
    key="discover_minutes",
    on_change=reset_selection,
)

filtered = position_pool[
    position_pool["minutes"] >= minimum_minutes
].copy()

if selected_team != "All teams":
    filtered = filtered[
        filtered["team_name"] == selected_team
    ]


# discover available statistical metrics
available_metrics = sorted(
    column
    for column in eligible.columns
    if column.endswith("_per90")
    and pd.api.types.is_numeric_dtype(eligible[column])
)

metric_options = {"No metric filter": None}

for metric in available_metrics:
    metric_options[metric_label(metric)] = metric


# advanced statistical search
st.sidebar.divider()

with st.sidebar.expander(
    "Advanced Statistical Search",
    expanded=False,
):
    st.caption(
        "Filter players by recorded values and "
        "positional percentile rankings."
    )

    first_label = st.selectbox(
        "Primary metric",
        list(metric_options),
        key="discover_metric_a",
        on_change=reset_selection,
    )

    first_metric = metric_options[first_label]
    first_value = 0.0
    first_percentile = 0

    if first_metric is not None:
        first_value = st.number_input(
            "Minimum value per 90",
            min_value=0.0,
            value=0.0,
            step=0.1,
            key="discover_value_a",
            on_change=reset_selection,
        )

        first_percentile = st.slider(
            "Minimum percentile",
            min_value=0,
            max_value=100,
            value=0,
            step=5,
            key="discover_percentile_a",
            on_change=reset_selection,
        )

    second_options = {
        label: metric
        for label, metric in metric_options.items()
        if metric is None or metric != first_metric
    }

    if st.session_state.get("discover_metric_b") not in second_options:
        st.session_state["discover_metric_b"] = "No metric filter"

    second_label = st.selectbox(
        "Secondary metric",
        list(second_options),
        key="discover_metric_b",
        on_change=reset_selection,
    )

    second_metric = second_options[second_label]
    second_value = 0.0
    second_percentile = 0

    if second_metric is not None:
        second_value = st.number_input(
            "Minimum secondary value per 90",
            min_value=0.0,
            value=0.0,
            step=0.1,
            key="discover_value_b",
            on_change=reset_selection,
        )

        second_percentile = st.slider(
            "Minimum secondary percentile",
            min_value=0,
            max_value=100,
            value=0,
            step=5,
            key="discover_percentile_b",
            on_change=reset_selection,
        )



# calculate percentiles using players with at least 900 minutes
selected_metrics = [
    metric
    for metric in (first_metric, second_metric)
    if metric is not None
]

if selected_metrics:
    reference = calculate_percentiles(
        ranking_pool,
        tuple(selected_metrics),
    )

    # assign percentile ranks to eligible players
    for metric in selected_metrics:
        percentile_column = f"pct__{metric}"

        filtered[percentile_column] = (
            reference[percentile_column]
            .reindex(filtered.index)
        )


# apply statistical filters
for metric, min_value, min_percentile in [
    (first_metric, first_value, first_percentile),
    (second_metric, second_value, second_percentile),
]:
    if metric is None:
        continue

    # filter by recorded statistical value
    filtered = filtered[
        filtered[metric].notna()
        & (filtered[metric] >= min_value)
    ].copy()

    # apply percentile filter only when a threshold is selected
    if min_percentile > 0:
        filtered = filtered[
            filtered[f"pct__{metric}"] >= min_percentile
        ].copy()

# sort the discovery results
if first_metric is not None:
    filtered = filtered.sort_values(
        [f"pct__{first_metric}", first_metric],
        ascending=[False, False],
    )
else:
    filtered = filtered.sort_values("player_name")


# player discovery summary
st.subheader("Player Discovery")

col1, col2, col3 = st.columns(3)

col1.metric("Matching Players", len(filtered))
col2.metric("Available Positions", filtered["primary_position_group"].nunique())
col3.metric("Teams Represented", filtered["team_name"].nunique())

st.divider()


# display ranked discovery table
if filtered.empty:
    st.warning(
        "No players match your filters. "
        "Try lowering the statistical thresholds."
    )

else:
    columns = [
        "player_name",
        "team_name",
        "primary_position_group",
        "minutes",
    ]

    for metric in selected_metrics:
        columns.extend([
            metric,
            f"pct__{metric}",
        ])

    results = filtered[columns].copy()

    column_names = {
        "player_name": "Player",
        "team_name": "Team",
        "primary_position_group": "Position",
        "minutes": "Minutes",
    }

    for metric in selected_metrics:
        column_names[metric] = f"{metric_label(metric)} /90"
        column_names[f"pct__{metric}"] = (
            f"{metric_label(metric)} Percentile"
        )

    results = results.rename(columns=column_names)

    numeric_columns = results.select_dtypes(
        include="number"
    ).columns

    st.dataframe(
        results.style.format({
            column: "{:.2f}"
            for column in numeric_columns
        }),
        hide_index=True,
        use_container_width=True,
        height=400,
    )


# searchable player dropdown

# quick scouting preview for discovered players
st.divider()
st.subheader("🔎 Quick Scouting Preview")

st.caption(
    "Select a player to inspect their scouting statistics "
    "before opening their complete profile."
)

# searchable player selection
selected_index = st.selectbox(
    "Search or select a player",
    options=filtered.index.tolist(),
    index=None,
    placeholder="Start typing a player's name...",
    format_func=lambda i: filtered.loc[i, "player_label"],
    key="discover_player",
    disabled=filtered.empty,
)

if selected_index is not None:
    player = filtered.loc[selected_index]

    player_name = str(player["player_name"])
    position = str(player["primary_position_group"])
    minutes = float(player["minutes"])

    # display a compact scouting identity card
    with st.container(border=True):
        st.subheader(player_name)

        st.caption(
            f"{player['team_name']} | {position}"
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Minutes Played",
            f"{minutes:,.2f}",
        )

        col2.metric(
            "Position",
            position,
        )

        col3.metric(
            "Ranking Status",
            "Eligible" if minutes >= 900 else "Limited Data",
        )

    # choose position-specific scouting metrics
    profile_metrics = [
        metric
        for metric in SCOUTING_PROFILES.get(position, [])
        if metric in df.columns
    ]

    # use all eligible positional peers as the reference
    reference = df[
        (df["minutes"] >= 900)
        & (df["primary_position_group"] == position)
    ].copy()

    preview_rows = []

    for metric in profile_metrics:
        value = player.get(metric)

        if pd.isna(value):
            continue

        percentile = None

        # only rank players meeting the minutes requirement
        if minutes >= 900 and not reference.empty:
            ranks = (
                reference[metric]
                .rank(method="average", pct=True)
                .mul(100)
            )

            rank = ranks.get(player.name)

            if pd.notna(rank):
                percentile = float(rank)

        preview_rows.append({
            "Metric": metric_label(metric),
            "Value /90": float(value),
            "Percentile": percentile,
        })

    # display compact statistical preview
    st.markdown("#### Performance Snapshot")

    if preview_rows:
        preview_df = pd.DataFrame(preview_rows)

        st.dataframe(
            preview_df.style.format({
                "Value /90": "{:.2f}",
                "Percentile": lambda value: (
                    f"{value:.2f}"
                    if pd.notna(value)
                    else "Not ranked"
                ),
            }),
            hide_index=True,
            use_container_width=True,
        )

        # show percentile performance chart when available
        ranked_preview = preview_df.dropna(
            subset=["Percentile"]
        )

        if not ranked_preview.empty:
            st.bar_chart(
                ranked_preview.set_index("Metric")[
                    "Percentile"
                ],
                horizontal=True,
                x_label="Metric",
                y_label="Percentile Rank",
            )

    else:
        st.info(
            "No position-specific metrics are available "
            "for this player."
        )

    if minutes < 900:
        st.info(
            "This player has fewer than 900 recorded minutes. "
            "Their per-90 statistics are displayed, but "
            "positional percentile rankings are unavailable."
        )

    # save selection for the player profile page
    st.session_state["selected_player_id"] = int(
        player["player_id"]
    )

    st.session_state["selected_team_id"] = int(
        player["team_id"]
    )

    # open the detailed player profile
    if st.button(
        "View Full Player Profile",
        type="primary",
        use_container_width=True,
    ):
        st.switch_page("pages/Player_Profile.py")

# footer
st.divider()

st.caption(
    "ScoutLocal | Player Discovery | StatsBomb Open Data"
)
