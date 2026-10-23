from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

from scoutlocal.metrics.profiles import SCOUTING_PROFILES
from scoutlocal.reports.comparison_report import generate_comparison_report
from scoutlocal.reports.report_builder import build_player_report


# configure the dashboard
st.set_page_config(page_title="ScoutLocal", page_icon="⚽", layout="wide")

DATA_PATH = Path(__file__).resolve().parent / "data" / "player_metrics_with_positions.csv"
MIN_MINUTES = 900


# load season data
@st.cache_data
def load_players():
    return pd.read_csv(DATA_PATH)


# format metric labels for the dashboard
def metric_label(metric):
    return metric.removesuffix("_per90").replace("_", " ").title()


# dashboard branding
st.markdown(
    """
<div style="padding:24px 28px;background:linear-gradient(120deg,#16243A,#0B1423);border:1px solid #263852;border-radius:14px;margin-bottom:20px;">
    <div style="color:#60A5FA;font-size:12px;font-weight:700;letter-spacing:2px;">FOOTBALL INTELLIGENCE PLATFORM</div>
    <h1 style="color:white;font-size:38px;margin:10px 0;">SCOUTLOCAL</h1>
    <p style="color:#A8BCD3;font-size:15px;margin:0;">Data-driven scouting | Indian Super League 2021/22</p>
</div>
    """,
    unsafe_allow_html=True,
)


# filter to eligible players with supported position profiles
try:
    df = load_players()
except FileNotFoundError:
    st.error(f"Player data file not found: {DATA_PATH}")
    st.stop()

eligible = df[
    (df["minutes"] >= MIN_MINUTES)
    & df["primary_position_group"].isin(SCOUTING_PROFILES.keys())
].copy()

if eligible.empty:
    st.error("No eligible players found in the season data.")
    st.stop()

eligible["player_label"] = (
    eligible["player_name"].astype(str)
    + " | "
    + eligible["team_name"].astype(str)
    + " | ID "
    + eligible["player_id"].astype(str)
)


# clear selected players whenever the search filters change
# callbacks run before Streamlit recreates its dropdown widgets
def clear_player_selections():
    st.session_state.pop("player_search_dropdown", None)
    st.session_state.pop("comparison_search_dropdown", None)


# rank a metric against the fixed 900-minute positional peer group
# this matches the rank(pct=True, method="average") convention in the reports
@st.cache_data
def build_metric_percentiles(players, metrics):
    ranked = players.copy()
    for metric in metrics:
        ranked[f"pct__{metric}"] = (
            ranked.groupby("primary_position_group")[metric]
            .rank(method="average", pct=True)
            .mul(100)
        )
    return ranked


# filter the player pool before searching by name
st.sidebar.header("Player Filters")

position_choices = ["All positions"] + sorted(
    eligible["primary_position_group"].dropna().unique().tolist()
)
selected_position = st.sidebar.selectbox(
    "Position",
    position_choices,
    key="filter_position",
    on_change=clear_player_selections,
)

position_pool = eligible
if selected_position != "All positions":
    position_pool = eligible[
        eligible["primary_position_group"] == selected_position
    ]

team_choices = ["All teams"] + sorted(
    position_pool["team_name"].dropna().unique().tolist()
)

# prevent a stale team selection after changing position
if st.session_state.get("filter_team", "All teams") not in team_choices:
    st.session_state["filter_team"] = "All teams"

selected_team = st.sidebar.selectbox(
    "Team",
    team_choices,
    key="filter_team",
    on_change=clear_player_selections,
)

minimum_minutes = st.sidebar.number_input(
    "Minimum minutes played",
    min_value=MIN_MINUTES,
    value=MIN_MINUTES,
    step=100,
    key="filter_minimum_minutes",
    on_change=clear_player_selections,
    help=(
        "Filters which players you can select. The report's positional "
        "percentiles still use the fixed 900-minute eligibility threshold."
    ),
)

filtered_players = position_pool[
    position_pool["minutes"] >= minimum_minutes
].copy()
if selected_team != "All teams":
    filtered_players = filtered_players[
        filtered_players["team_name"] == selected_team
    ]

# build the percentile reference using ALL eligible 900-minute players,
# before applying search filters, so peer rankings remain consistent
available_metrics = sorted(
    column for column in eligible.columns
    if column.endswith("_per90")
    and pd.api.types.is_numeric_dtype(eligible[column])
)

# advanced metric discovery
st.sidebar.divider()
with st.sidebar.expander("Advanced Statistical Search", expanded=True):
    st.caption(
        "Combine up to two statistical requirements. All thresholds are "
        "optional, and both conditions must be satisfied."
    )

    metric_options = {"No metric filter": None}
    metric_options.update({metric_label(m): m for m in available_metrics})
    metric_labels = list(metric_options)

    first_metric_label = st.selectbox(
        "Primary statistical metric",
        options=metric_labels,
        key="advanced_metric_a",
        on_change=clear_player_selections,
    )
    first_metric = metric_options[first_metric_label]
    first_min_value = 0.0
    first_min_percentile = 0
    if first_metric is not None:
        first_min_value = st.number_input(
            "Minimum recorded value per 90 (primary)",
            min_value=0.0,
            value=0.0,
            step=0.1,
            format="%.2f",
            key="advanced_value_a",
            on_change=clear_player_selections,
        )
        first_min_percentile = st.slider(
            "Minimum positional percentile (primary)",
            min_value=0,
            max_value=100,
            value=0,
            step=5,
            key="advanced_percentile_a",
            on_change=clear_player_selections,
        )

    second_metric_labels = ["No metric filter"] + [
        label for label in metric_labels[1:] if metric_options[label] != first_metric
    ]
    if st.session_state.get("advanced_metric_b") not in second_metric_labels:
        st.session_state["advanced_metric_b"] = "No metric filter"
    second_metric_label = st.selectbox(
        "Secondary statistical metric (optional)",
        options=second_metric_labels,
        key="advanced_metric_b",
        on_change=clear_player_selections,
    )
    second_metric = metric_options[second_metric_label]
    second_min_value = 0.0
    second_min_percentile = 0
    if second_metric is not None:
        second_min_value = st.number_input(
            "Minimum recorded value per 90 (secondary)",
            min_value=0.0,
            value=0.0,
            step=0.1,
            format="%.2f",
            key="advanced_value_b",
            on_change=clear_player_selections,
        )
        second_min_percentile = st.slider(
            "Minimum positional percentile (secondary)",
            min_value=0,
            max_value=100,
            value=0,
            step=5,
            key="advanced_percentile_b",
            on_change=clear_player_selections,
        )

selected_metrics = [m for m in (first_metric, second_metric) if m is not None]
if selected_metrics:
    ranking_reference = build_metric_percentiles(eligible, tuple(selected_metrics))
    for metric in selected_metrics:
        filtered_players[f"pct__{metric}"] = ranking_reference.loc[
            filtered_players.index, f"pct__{metric}"
        ]

    for metric, minimum_value, minimum_pct in (
        (first_metric, first_min_value, first_min_percentile),
        (second_metric, second_min_value, second_min_percentile),
    ):
        if metric is None:
            continue
        filtered_players = filtered_players[
            filtered_players[metric].notna()
            & (filtered_players[metric] >= minimum_value)
            & (filtered_players[f"pct__{metric}"] >= minimum_pct)
        ]

if first_metric:
    filtered_players = filtered_players.sort_values(
        [f"pct__{first_metric}", first_metric, "player_name"],
        ascending=[False, False, True],
    )
else:
    filtered_players = filtered_players.sort_values("player_name")

st.sidebar.metric("Matching players", len(filtered_players))

# show matching player records and the metrics used to rank them
with st.sidebar.expander("View matching players", expanded=False):
    if filtered_players.empty:
        st.warning("No eligible players match the filters. Lower your thresholds.")
    else:
        summary_columns = [
            "player_name", "team_name", "primary_position_group", "minutes"
        ] + [value for m in selected_metrics for value in (m, f"pct__{m}")]
        summary_names = {
            "player_name": "Player",
            "team_name": "Team",
            "primary_position_group": "Position",
            "minutes": "Minutes",
        }
        for m in selected_metrics:
            summary_names[m] = f"{metric_label(m)} /90"
            summary_names[f"pct__{m}"] = f"{metric_label(m)} percentile"
        result_table = filtered_players[summary_columns].rename(columns=summary_names)
        numeric_columns = {
            name: "{:.2f}" for name in result_table.columns
            if name not in ("Player", "Team", "Position")
        }
        st.dataframe(
            result_table.style.format(numeric_columns),
            hide_index=True,
            use_container_width=True,
            height=240,
        )

# a larger discovery table is useful before selecting an individual player
st.subheader("Player Discovery")
st.caption(
    "Results update immediately as you adjust the sidebar. "
    "Ranked by the primary metric's percentile when one is selected."
)
if filtered_players.empty:
    st.warning("No matching players. Try a different position or lower the thresholds.")
else:
    results_columns = [
        "player_name", "team_name", "primary_position_group", "minutes"
    ] + [value for m in selected_metrics for value in (m, f"pct__{m}")]
    results_names = {
        "player_name": "Player", "team_name": "Team",
        "primary_position_group": "Position", "minutes": "Minutes"
    }
    for m in selected_metrics:
        results_names[m] = f"{metric_label(m)} /90"
        results_names[f"pct__{m}"] = f"{metric_label(m)} pct"
    results_df = filtered_players[results_columns].rename(columns=results_names)
    display_formats = {
        col: "{:.2f}" for col in results_df.columns
        if col not in ("Player", "Team", "Position")
    }
    st.dataframe(
        results_df.style.format(display_formats),
        hide_index=True, use_container_width=True, height=330,
    )
    st.caption(f"{len(filtered_players)} matching player-team records")

st.caption(
    "Advanced percentiles are computed against the fixed 900-minute positional "
    "peer groups, not recalculated from filtered results. Statistical activity "
    "is not an overall quality rating."
)

# autocomplete search uses only the remaining filtered records
st.sidebar.divider()
st.sidebar.header("Player Search")

selected_index = st.sidebar.selectbox(
    "Search and select player",
    options=filtered_players.index.tolist(),
    index=None,
    placeholder="Type a player name...",
    format_func=lambda i: filtered_players.loc[i, "player_label"],
    key="player_search_dropdown",
    disabled=filtered_players.empty,
)

if selected_index is None:
    st.info(
        "Choose a player from the searchable dropdown to open their profile. "
        "The discovery results above can be explored without selecting a player."
    )
    st.stop()

selected_player = filtered_players.loc[selected_index]

# report builder currently accepts a unique player id only
# avoid crashing when the same id appears on multiple team rows
selected_id = int(selected_player["player_id"])
if (df["player_id"] == selected_id).sum() > 1:
    st.warning(
        "This player has records for more than one team. "
        "Team-specific report selection is not implemented yet."
    )
    st.stop()

try:
    report = build_player_report(selected_id)
except (ValueError, KeyError) as error:
    st.error(f"Unable to generate the player report: {error}")
    st.stop()


# choose an optional second player for comparison
st.sidebar.divider()
st.sidebar.header("Compare Players")

comparison_options = eligible[
    (eligible["primary_position_group"] == selected_player["primary_position_group"])
    & ~(
        (eligible["player_id"] == selected_player["player_id"])
        & (eligible["team_id"] == selected_player["team_id"])
    )
].copy()

comparison_team_choices = ["All teams"] + sorted(
    comparison_options["team_name"].dropna().unique().tolist()
)
comparison_team = st.sidebar.selectbox(
    "Comparison team", comparison_team_choices, key="comparison_team"
)
if comparison_team != "All teams":
    comparison_options = comparison_options[
        comparison_options["team_name"] == comparison_team
    ]

# second autocomplete dropdown, limited to same-position players
compare_index = st.sidebar.selectbox(
    "Search and select comparison player (optional)",
    options=comparison_options.index.tolist(),
    index=None,
    placeholder="Type a second player name...",
    format_func=lambda i: comparison_options.loc[i, "player_label"],
    key="comparison_search_dropdown",
)

compare_report = None
if compare_index is not None:
    compare_player = comparison_options.loc[compare_index]
    compare_id = int(compare_player["player_id"])
    if (df["player_id"] == compare_id).sum() > 1:
        st.sidebar.warning(
            "This player has multiple team records and cannot yet be compared."
        )
    else:
        try:
            compare_report = build_player_report(compare_id)
        except (ValueError, KeyError) as error:
            st.sidebar.error(f"Could not load comparison player: {error}")
else:
    st.sidebar.caption("Leave blank to view a single player's report.")


# organize the scouting dashboard into tabs
profile_tab, insights_tab, comparison_tab = st.tabs(
    ["Player Profile", "Scouting Insights", "Player Comparison"]
)


# player profile tab
with profile_tab:
    player_name = escape(str(report["player_name"]))
    team_name = escape(str(report["team_name"]))
    position_name = escape(str(report["position"]))

    st.markdown(
        f"""
<div style="background:#16243A;border:1px solid #263852;border-radius:12px;padding:24px;margin-bottom:20px;">
    <div style="color:#60A5FA;font-size:12px;font-weight:700;letter-spacing:2px;">PLAYER SCOUTING PROFILE</div>
    <h2 style="color:white;font-size:30px;margin:12px 0 8px 0;">{player_name}</h2>
    <p style="color:#A8BCD3;font-size:15px;margin:0;">{team_name} | {position_name}</p>
</div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Minutes Played", f"{report['minutes']:,.2f}")
    col2.metric("Eligible Peers", report["peer_count"])
    col3.metric("Metrics Analysed", len(report["all_metrics"]))

    st.divider()
    st.subheader("Scouting Profile")

    metrics_df = pd.DataFrame(report["all_metrics"]).copy()
    metrics_df["metric"] = metrics_df["metric"].map(metric_label)
    display_df = metrics_df.rename(
        columns={
            "metric": "Metric",
            "value": "Value",
            "percentile": "Percentile Rank",
        }
    )

    st.dataframe(
        display_df.style.format({"Value": "{:.2f}", "Percentile Rank": "{:.2f}"}),
        hide_index=True,
        use_container_width=True,
    )

    st.subheader("Positional Percentiles")
    st.bar_chart(
        metrics_df.set_index("metric")["percentile"],
        horizontal=True,
        x_label="Metric",
        y_label="Percentile Rank",
    )
    st.caption(
        "Percentiles measure recorded statistical activity relative to eligible "
        "players in the same positional group."
    )


# scouting insights tab
with insights_tab:
    st.header("Scouting Insights")
    st.write(f"Statistical observations for **{report['player_name']}**.")

    strongest = report["strongest_metrics"][0]
    lowest = report["lowest_metrics"][0]
    left_col, right_col = st.columns(2)

    with left_col:
        with st.container(border=True):
            st.caption("HIGHEST-RANKED METRIC")
            st.subheader(metric_label(strongest["metric"]))
            st.metric("Percentile Rank", f"{strongest['percentile']:.2f}")
            st.write(f"Recorded value: {strongest['value']:.2f} per 90 minutes")

    with right_col:
        with st.container(border=True):
            st.caption("LOWEST-RANKED METRIC")
            st.subheader(metric_label(lowest["metric"]))
            st.metric("Percentile Rank", f"{lowest['percentile']:.2f}")
            st.write(f"Recorded value: {lowest['value']:.2f} per 90 minutes")

    st.divider()
    st.subheader("Scouting Observations")
    for observation in report["observations"]:
        st.write(f"• {observation}")

    st.info(
        "Higher or lower action volume does not necessarily indicate better or "
        "worse overall player quality."
    )


# player comparison tab
with comparison_tab:
    st.header("Player Comparison")

    if compare_report is None:
        st.info(
            "Search for a second eligible player in the sidebar to see "
            "a positional comparison."
        )
    else:
        left_col, right_col = st.columns(2)
        with left_col:
            st.subheader(report["player_name"])
            st.caption(f"{report['team_name']} | {report['position']}")
        with right_col:
            st.subheader(compare_report["player_name"])
            st.caption(f"{compare_report['team_name']} | {compare_report['position']}")

        comparison = generate_comparison_report(report, compare_report)
        comparison_rows = []
        percentile_rows = []

        for item in comparison["metrics"]:
            name = metric_label(item["metric"])
            comparison_rows.append(
                {
                    "Metric": name,
                    "Player A": item["player_a_value"],
                    "Player B": item["player_b_value"],
                }
            )
            percentile_rows.append(
                {
                    "Metric": name,
                    report["player_name"]: item["player_a_percentile"],
                    compare_report["player_name"]: item["player_b_percentile"],
                }
            )

        st.subheader("Statistics per 90 Minutes")
        st.caption(
            f"Player A: {report['player_name']} | "
            f"Player B: {compare_report['player_name']}"
        )
        comparison_df = pd.DataFrame(comparison_rows)
        st.dataframe(
            comparison_df.style.format(
                {"Player A": "{:.2f}", "Player B": "{:.2f}"}
            ),
            hide_index=True,
            use_container_width=True,
        )

        st.subheader("Positional Percentile Comparison")
        percentile_df = pd.DataFrame(percentile_rows).set_index("Metric")
        st.bar_chart(
            percentile_df,
            x_label="Metric",
            y_label="Percentile Rank",
            horizontal=True,
            stack=False,
        )
        st.caption(
            "Both players are ranked against eligible peers in the same "
            "positional group. The chart shows percentile ranks, not raw statistics."
        )


# dashboard footer
st.divider()
st.caption("ScoutLocal V0.1 | StatsBomb Open Data | Indian Super League 2021/22")
